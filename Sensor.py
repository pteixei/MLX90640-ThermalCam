"""
`adafruit_mlx90640`
================================================================================

Driver for the MLX90640 thermal camera 


* Author(s): ladyada

* with many changes to make it usable in micropython, done by many people

Implementation Notes
--------------------

**Software and Dependencies:**

TODO LIST:

    - Decide if mlx90640Frame should be moved back into getFrame method - mesuring available RAM - 
      and make sure to use there gc.collect() to clean 

ERRORS:

"""

import struct
import math
import time
from machine import I2C, Pin
import gc

__version__ = "0.0.0-auto.0"

# We match the melexis library naming, and don't want to change

# Hardware data
I2C_READ_LEN = const(2048)
SCALEALPHA = const(0.000001)
MLX90640_DEVICEID1 = const(0x2407)
OPENAIR_TA_SHIFT = const(8)
I2C_SDA = const(6)
I2C_SCL = const(7)
DEVICE_ADDRESS = const(0x33)
FRAME_SIZE = const(768)

# Buffers
global frame
frame = [0] * FRAME_SIZE
mlx90640Frame = [0] * 834                   # Move to GetFrame and use gc.collect() after usage

# Flags
global frame_lock, sensor_running
frame_lock = False
sensor_running = True

class Lock:
    def __init__(self):
        self._locked = frame_lock

    def acquire(self, timeout=0):
        """
            Tries to acquire the lock in the specified time).

                :param timeout: Maximum time (in seconds) to try to get the lock.
                        If timeout=0, tries to get immediately.
                :return: True if lock acquired.
        """
        start_time = time.time()
        
        while True:
            if not self._locked:
                self._locked = True
                return True
            if timeout > 0 and (time.time() - start_time) >= timeout:
                return False
            # wait to avoid excessive CPU use
            time.sleep(0.01)  # 10 ms

    def release(self):
        """
            Liberate lock.
        """
        self._locked = False


class RefreshRate:  # pylint: disable=too-few-public-methods
    """Enum-like class for MLX90640's refresh rate"""

    REFRESH_0_5_HZ = 0b000  # 0.5Hz
    REFRESH_1_HZ = 0b001  # 1Hz
    REFRESH_2_HZ = 0b010  # 2Hz
    REFRESH_4_HZ = 0b011  # 4Hz
    REFRESH_8_HZ = 0b100  # 8Hz
    REFRESH_16_HZ = 0b101  # 16Hz
    REFRESH_32_HZ = 0b110  # 32Hz
    REFRESH_64_HZ = 0b111  # 64Hz


class Sensor:  # pylint: disable=too-many-instance-attributes
    """Interface to the MLX90640 temperature sensor."""

    kVdd = 0
    vdd25 = 0
    KvPTAT = 0
    KtPTAT = 0
    vPTAT25 = 0
    alphaPTAT = 0
    gainEE = 0
    tgc = 0
    KsTa = 0
    resolutionEE = 0
    calibrationModeEE = 0
    ksTo = [0] * 5
    ct = [0] * 5
    alpha = [0] * 768
    alphaScale = 0
    offset = [0] * 768
    kta = [0] * 768
    ktaScale = 0
    kv = [0] * 768
    kvScale = 0
    cpAlpha = [0] * 2
    cpOffset = [0] * 2
    ilChessC = [0] * 3
    brokenPixels = []
    outlierPixels = []
    cpKta = 0
    cpKv = 0
    
    eeData = [0] * 832
    
    inbuf = memoryview(bytearray(I2C_READ_LEN*2))

    def __init__(self):
        self._frame_lock = Lock()
        self.timeout = 1
        self.device_address = DEVICE_ADDRESS
        self.i2c_device = I2C(1, scl=Pin(I2C_SCL, Pin.OUT), sda=Pin(I2C_SDA, Pin.OUT), freq=400000)
        self._I2CReadWords(0x2400, self.eeData)
        self._ExtractParameters()
        print("MLX addr detected on I2C")
        print("Sensor ID:", [hex(i) for i in self.serial_number])
        gc.collect()     

    @property
    def serial_number(self):
        """3-item tuple of hex values that are unique to each MLX90640"""
        serialWords = [0, 0, 0]
        self._I2CReadWords(MLX90640_DEVICEID1, serialWords)
        return serialWords

    @property
    def refresh_rate(self):
        """How fast the MLX90640 will spit out data. Start at lowest speed in
        RefreshRate and then slowly increase I2C clock rate and rate until you
        max out. The sensor does not like it if the I2C host cannot 'keep up'!"""
        controlRegister = [0]
        self._I2CReadWords(0x800D, controlRegister)
        return (controlRegister[0] >> 7) & 0x07

    @refresh_rate.setter
    def refresh_rate(self, rate):
        controlRegister = [0]
        value = (rate & 0x7) << 7
        self._I2CReadWords(0x800D, controlRegister)
        value |= controlRegister[0] & 0xFC7F
        self._I2CWriteWord(0x800D, value)

    def getFrame(self, framebuf=frame):
        """Request both 'halves' of a frame from the sensor, merge them
        and calculate the temperature in degrees C for each of 32x24 pixels. Placed
        into framebuffer, the 768-element array passed in"""
                
        emissivity = 0.95
        tr = 23.15
        
        for _ in range(2):
            status = self._GetFrameData(mlx90640Frame)
            if status < 0:
                raise RuntimeError("Frame data error")
            # For a MLX90640 in the open air the shift is -8 degC.
            tr = self._GetTa(mlx90640Frame) - OPENAIR_TA_SHIFT
            self._CalculateTo(mlx90640Frame, emissivity, tr, framebuf)            

    def _GetFrameData(self, frameData):
        dataReady = 0
        cnt = 0
        statusRegister = [0]
        controlRegister = [0]

        while dataReady == 0:
            self._I2CReadWords(0x8000, statusRegister)
            dataReady = statusRegister[0] & 0x0008

        while (dataReady != 0) and (cnt < 5):
            self._I2CWriteWord(0x8000, 0x0030)
            self._I2CReadWords(0x0400, frameData, end=832)
            self._I2CReadWords(0x8000, statusRegister)
            dataReady = statusRegister[0] & 0x0008
            cnt += 1

        if cnt > 4:
            raise RuntimeError("Too many retries")

        self._I2CReadWords(0x800D, controlRegister)
        frameData[832] = controlRegister[0]
        frameData[833] = statusRegister[0] & 0x0001
        return frameData[833]

    def _GetTa(self, frameData):
        vdd = self._GetVdd(frameData)

        ptat = frameData[800]
        if ptat > 32767:
            ptat -= 65536

        ptatArt = frameData[768]
        if ptatArt > 32767:
            ptatArt -= 65536
        ptatArt = (ptat / (ptat * self.alphaPTAT + ptatArt)) * math.pow(2, 18)

        ta = ptatArt / (1 + self.KvPTAT * (vdd - 3.3)) - self.vPTAT25
        ta = ta / self.KtPTAT + 25
        return ta

    def _GetVdd(self, frameData):
        vdd = frameData[810]
        if vdd > 32767:
            vdd -= 65536

        resolutionRAM = (frameData[832] & 0x0C00) >> 10
        resolutionCorrection = math.pow(2, self.resolutionEE) / math.pow(
            2, resolutionRAM
        )
        vdd = (resolutionCorrection * vdd - self.vdd25) / self.kVdd + 3.3

        return vdd

    def _frame_locked(self, register, index, value):
        if self._frame_lock.acquire(self.timeout):
            try:
                register[index] = value
            finally:
                self._frame_lock.release()
                result = False
        else:
            raise Exception("Buffer in use by other process.")
            result = True
        return result

    def _CalculateTo(self, frameData, emissivity, tr, result):
        # pylint: disable=too-many-locals, too-many-branches, too-many-statements
        subPage = frameData[833]
        alphaCorrR = [0] * 4
        irDataCP = [0, 0]

        vdd = self._GetVdd(frameData)
        ta = self._GetTa(frameData)

        ta4 = ta + 273.15
        ta4 = ta4 * ta4
        ta4 = ta4 * ta4
        tr4 = tr + 273.15
        tr4 = tr4 * tr4
        tr4 = tr4 * tr4
        taTr = tr4 - (tr4 - ta4) / emissivity

        ktaScale = math.pow(2, self.ktaScale)
        kvScale = math.pow(2, self.kvScale)
        alphaScale = math.pow(2, self.alphaScale)

        alphaCorrR[0] = 1 / (1 + self.ksTo[0] * 40)
        alphaCorrR[1] = 1
        alphaCorrR[2] = 1 + self.ksTo[1] * self.ct[2]
        alphaCorrR[3] = alphaCorrR[2] * (1 + self.ksTo[2] * (self.ct[3] - self.ct[2]))

        # --------- Gain calculation -----------------------------------
        gain = frameData[778]
        if gain > 32767:
            gain -= 65536
        gain = self.gainEE / gain

        # --------- To calculation -------------------------------------
        mode = (frameData[832] & 0x1000) >> 5

        irDataCP[0] = frameData[776]
        irDataCP[1] = frameData[808]
        for i in range(2):
            if irDataCP[i] > 32767:
                irDataCP[i] -= 65536
            irDataCP[i] *= gain

        irDataCP[0] -= (
            self.cpOffset[0]
            * (1 + self.cpKta * (ta - 25))
            * (1 + self.cpKv * (vdd - 3.3))
        )
        if mode == self.calibrationModeEE:
            irDataCP[1] -= (
                self.cpOffset[1]
                * (1 + self.cpKta * (ta - 25))
                * (1 + self.cpKv * (vdd - 3.3))
            )
        else:
            irDataCP[1] -= (
                (self.cpOffset[1] + self.ilChessC[0])
                * (1 + self.cpKta * (ta - 25))
                * (1 + self.cpKv * (vdd - 3.3))
            )

        for pixelNumber in range(768):
            if self._IsPixelBad(pixelNumber):
                if self._frame_locked(result,pixelNumber, -273.15):
                    continue

            ilPattern = pixelNumber // 32 - (pixelNumber // 64) * 2
            chessPattern = ilPattern ^ (pixelNumber - (pixelNumber // 2) * 2)
            conversionPattern = (
                (pixelNumber + 2) // 4
                - (pixelNumber + 3) // 4
                + (pixelNumber + 1) // 4
                - pixelNumber // 4
            ) * (1 - 2 * ilPattern)

            if mode == 0:
                pattern = ilPattern
            else:
                pattern = chessPattern

            if pattern == frameData[833]:
                irData = frameData[pixelNumber]
                if irData > 32767:
                    irData -= 65536
                irData *= gain

                kta = self.kta[pixelNumber] / ktaScale
                kv = self.kv[pixelNumber] / kvScale
                irData -= (
                    self.offset[pixelNumber]
                    * (1 + kta * (ta - 25))
                    * (1 + kv * (vdd - 3.3))
                )

                if mode != self.calibrationModeEE:
                    irData += (
                        self.ilChessC[2] * (2 * ilPattern - 1)
                        - self.ilChessC[1] * conversionPattern
                    )

                irData = irData - self.tgc * irDataCP[subPage]
                irData /= emissivity

                alphaCompensated = SCALEALPHA * alphaScale / self.alpha[pixelNumber]
                alphaCompensated *= 1 + self.KsTa * (ta - 25)

                Sx = (
                    alphaCompensated
                    * alphaCompensated
                    * alphaCompensated
                    * (irData + alphaCompensated * taTr)
                )
                Sx = math.sqrt(math.sqrt(Sx)) * self.ksTo[1]

                To = (
                    math.sqrt(
                        math.sqrt(
                            irData
                            / (alphaCompensated * (1 - self.ksTo[1] * 273.15) + Sx)
                            + taTr
                        )
                    )
                    - 273.15
                )

                if To < self.ct[1]:
                    torange = 0
                elif To < self.ct[2]:
                    torange = 1
                elif To < self.ct[3]:
                    torange = 2
                else:
                    torange = 3

                To = (
                    math.sqrt(
                        math.sqrt(
                            irData
                            / (
                                alphaCompensated
                                * alphaCorrR[torange]
                                * (1 + self.ksTo[torange] * (To - self.ct[torange]))
                            )
                            + taTr
                        )
                    )
                    - 273.15
                )
                if self._frame_locked(result, pixelNumber, To):
                    continue

    # pylint: enable=too-many-locals, too-many-branches, too-many-statements

    def _ExtractParameters(self):
        self._ExtractVDDParameters()
        gc.collect()
        self._ExtractPTATParameters()
        gc.collect()
        self._ExtractGainParameters()
        gc.collect()
        self._ExtractTgcParameters()
        gc.collect()
        self._ExtractResolutionParameters()
        gc.collect()
        self._ExtractKsTaParameters()
        gc.collect()
        self._ExtractKsToParameters()
        gc.collect()
        self._ExtractCPParameters()
        gc.collect()
        self._ExtractAlphaParameters()
        gc.collect()
        self._ExtractOffsetParameters()
        gc.collect()
        self._ExtractKtaPixelParameters()
        gc.collect()
        self._ExtractKvPixelParameters()
        gc.collect()
        self._ExtractCILCParameters()
        gc.collect()
        self._ExtractDeviatingPixels()
        gc.collect()

    def _ExtractVDDParameters(self):
        # extract VDD
        self.kVdd = (self.eeData[51] & 0xFF00) >> 8
        if self.kVdd > 127:
            self.kVdd -= 256  # convert to signed
        self.kVdd *= 32
        self.vdd25 = self.eeData[51] & 0x00FF
        self.vdd25 = ((self.vdd25 - 256) << 5) - 8192

    def _ExtractPTATParameters(self):
        # extract PTAT
        self.KvPTAT = (self.eeData[50] & 0xFC00) >> 10
        if self.KvPTAT > 31:
            self.KvPTAT -= 64
        self.KvPTAT /= 4096
        self.KtPTAT = self.eeData[50] & 0x03FF
        if self.KtPTAT > 511:
            self.KtPTAT -= 1024
        self.KtPTAT /= 8
        self.vPTAT25 = self.eeData[49]
        self.alphaPTAT = (self.eeData[16] & 0xF000) / math.pow(2, 14) + 8

    def _ExtractGainParameters(self):
        # extract Gain
        self.gainEE = self.eeData[48]
        if self.gainEE > 32767:
            self.gainEE -= 65536

    def _ExtractTgcParameters(self):
        # extract Tgc
        self.tgc = self.eeData[60] & 0x00FF
        if self.tgc > 127:
            self.tgc -= 256
        self.tgc /= 32

    def _ExtractResolutionParameters(self):
        # extract resolution
        self.resolutionEE = (self.eeData[56] & 0x3000) >> 12

    def _ExtractKsTaParameters(self):
        # extract KsTa
        self.KsTa = (self.eeData[60] & 0xFF00) >> 8
        if self.KsTa > 127:
            self.KsTa -= 256
        self.KsTa /= 8192

    def _ExtractKsToParameters(self):
        # extract ksTo
        step = ((self.eeData[63] & 0x3000) >> 12) * 10
        self.ct[0] = -40
        self.ct[1] = 0
        self.ct[2] = (self.eeData[63] & 0x00F0) >> 4
        self.ct[3] = (self.eeData[63] & 0x0F00) >> 8
        self.ct[2] *= step
        self.ct[3] = self.ct[2] + self.ct[3] * step

        KsToScale = (self.eeData[63] & 0x000F) + 8
        KsToScale = 1 << KsToScale

        self.ksTo[0] = self.eeData[61] & 0x00FF
        self.ksTo[1] = (self.eeData[61] & 0xFF00) >> 8
        self.ksTo[2] = self.eeData[62] & 0x00FF
        self.ksTo[3] = (self.eeData[62] & 0xFF00) >> 8

        for i in range(4):
            if self.ksTo[i] > 127:
                self.ksTo[i] -= 256
            self.ksTo[i] /= KsToScale
        self.ksTo[4] = -0.0002

    def _ExtractCPParameters(self):
        # extract CP
        offsetSP = [0] * 2
        alphaSP = [0] * 2

        alphaScale = ((self.eeData[32] & 0xF000) >> 12) + 27

        offsetSP[0] = self.eeData[58] & 0x03FF
        if offsetSP[0] > 511:
            offsetSP[0] -= 1024

        offsetSP[1] = (self.eeData[58] & 0xFC00) >> 10
        if offsetSP[1] > 31:
            offsetSP[1] -= 64
        offsetSP[1] += offsetSP[0]

        alphaSP[0] = self.eeData[57] & 0x03FF
        if alphaSP[0] > 511:
            alphaSP[0] -= 1024
        alphaSP[0] /= math.pow(2, alphaScale)

        alphaSP[1] = (self.eeData[57] & 0xFC00) >> 10
        if alphaSP[1] > 31:
            alphaSP[1] -= 64
        alphaSP[1] = (1 + alphaSP[1] / 128) * alphaSP[0]

        cpKta = self.eeData[59] & 0x00FF
        if cpKta > 127:
            cpKta -= 256
        ktaScale1 = ((self.eeData[56] & 0x00F0) >> 4) + 8
        self.cpKta = cpKta / math.pow(2, ktaScale1)

        cpKv = (self.eeData[59] & 0xFF00) >> 8
        if cpKv > 127:
            cpKv -= 256
        kvScale = (self.eeData[56] & 0x0F00) >> 8
        self.cpKv = cpKv / math.pow(2, kvScale)

        self.cpAlpha[0] = alphaSP[0]
        self.cpAlpha[1] = alphaSP[1]
        self.cpOffset[0] = offsetSP[0]
        self.cpOffset[1] = offsetSP[1]

    def _ExtractAlphaParameters(self):
        # extract alpha
        accRemScale = self.eeData[32] & 0x000F
        accColumnScale = (self.eeData[32] & 0x00F0) >> 4
        accRowScale = (self.eeData[32] & 0x0F00) >> 8
        alphaScale = ((self.eeData[32] & 0xF000) >> 12) + 30
        alphaRef = self.eeData[33]
        accRow = [0] * 24
        accColumn = [0] * 32
        alphaTemp = [0] * 768

        for i in range(6):
            p = i * 4
            accRow[p + 0] = self.eeData[34 + i] & 0x000F
            accRow[p + 1] = (self.eeData[34 + i] & 0x00F0) >> 4
            accRow[p + 2] = (self.eeData[34 + i] & 0x0F00) >> 8
            accRow[p + 3] = (self.eeData[34 + i] & 0xF000) >> 12

        for i in range(24):
            if accRow[i] > 7:
                accRow[i] -= 16

        for i in range(8):
            p = i * 4
            accColumn[p + 0] = self.eeData[40 + i] & 0x000F
            accColumn[p + 1] = (self.eeData[40 + i] & 0x00F0) >> 4
            accColumn[p + 2] = (self.eeData[40 + i] & 0x0F00) >> 8
            accColumn[p + 3] = (self.eeData[40 + i] & 0xF000) >> 12

        for i in range(32):
            if accColumn[i] > 7:
                accColumn[i] -= 16

        for i in range(24):
            for j in range(32):
                p = 32 * i + j
                alphaTemp[p] = (self.eeData[64 + p] & 0x03F0) >> 4
                if alphaTemp[p] > 31:
                    alphaTemp[p] -= 64
                alphaTemp[p] *= 1 << accRemScale
                alphaTemp[p] += (
                    alphaRef
                    + (accRow[i] << accRowScale)
                    + (accColumn[j] << accColumnScale)
                )
                alphaTemp[p] /= math.pow(2, alphaScale)
                alphaTemp[p] -= self.tgc * (self.cpAlpha[0] + self.cpAlpha[1]) / 2
                alphaTemp[p] = SCALEALPHA / alphaTemp[p]
        # print("alphaTemp: ", alphaTemp)

        temp = max(alphaTemp)

        alphaScale = 0
        while temp < 32768:
            temp *= 2
            alphaScale += 1

        for i in range(768):
            temp = alphaTemp[i] * math.pow(2, alphaScale)
            self.alpha[i] = int(temp + 0.5)

        self.alphaScale = alphaScale

    def _ExtractOffsetParameters(self):
        # extract offset
        occRow = [0] * 24
        occColumn = [0] * 32

        occRemScale = self.eeData[16] & 0x000F
        occColumnScale = (self.eeData[16] & 0x00F0) >> 4
        occRowScale = (self.eeData[16] & 0x0F00) >> 8
        offsetRef = self.eeData[17]
        if offsetRef > 32767:
            offsetRef -= 65536

        for i in range(6):
            p = i * 4
            occRow[p + 0] = self.eeData[18 + i] & 0x000F
            occRow[p + 1] = (self.eeData[18 + i] & 0x00F0) >> 4
            occRow[p + 2] = (self.eeData[18 + i] & 0x0F00) >> 8
            occRow[p + 3] = (self.eeData[18 + i] & 0xF000) >> 12

        for i in range(24):
            if occRow[i] > 7:
                occRow[i] -= 16

        for i in range(8):
            p = i * 4
            occColumn[p + 0] = self.eeData[24 + i] & 0x000F
            occColumn[p + 1] = (self.eeData[24 + i] & 0x00F0) >> 4
            occColumn[p + 2] = (self.eeData[24 + i] & 0x0F00) >> 8
            occColumn[p + 3] = (self.eeData[24 + i] & 0xF000) >> 12

        for i in range(32):
            if occColumn[i] > 7:
                occColumn[i] -= 16

        for i in range(24):
            for j in range(32):
                p = 32 * i + j
                self.offset[p] = (self.eeData[64 + p] & 0xFC00) >> 10
                if self.offset[p] > 31:
                    self.offset[p] -= 64
                self.offset[p] *= 1 << occRemScale
                self.offset[p] += (
                    offsetRef
                    + (occRow[i] << occRowScale)
                    + (occColumn[j] << occColumnScale)
                )

    def _ExtractKtaPixelParameters(self):  # pylint: disable=too-many-locals
        # extract KtaPixel

        KtaRC = [0] * 4
        ktaTemp = [0] * 768

        KtaRoCo = (self.eeData[54] & 0xFF00) >> 8
        if KtaRoCo > 127:
            KtaRoCo -= 256
        KtaRC[0] = KtaRoCo

        KtaReCo = self.eeData[54] & 0x00FF
        if KtaReCo > 127:
            KtaReCo -= 256
        KtaRC[2] = KtaReCo

        KtaRoCe = (self.eeData[55] & 0xFF00) >> 8
        if KtaRoCe > 127:
            KtaRoCe -= 256
        KtaRC[1] = KtaRoCe

        KtaReCe = self.eeData[55] & 0x00FF
        if KtaReCe > 127:
            KtaReCe -= 256
        KtaRC[3] = KtaReCe

        ktaScale1 = ((self.eeData[56] & 0x00F0) >> 4) + 8
        ktaScale2 = self.eeData[56] & 0x000F

        for i in range(24):
            for j in range(32):
                p = 32 * i + j
                split = 2 * (p // 32 - (p // 64) * 2) + p % 2
                ktaTemp[p] = (self.eeData[64 + p] & 0x000E) >> 1
                if ktaTemp[p] > 3:
                    ktaTemp[p] -= 8
                ktaTemp[p] *= 1 << ktaScale2
                ktaTemp[p] += KtaRC[split]
                ktaTemp[p] /= math.pow(2, ktaScale1)

        temp = abs(ktaTemp[0])
        for kta in ktaTemp:
            temp = max(temp, abs(kta))

        ktaScale1 = 0
        while temp < 64:
            temp *= 2
            ktaScale1 += 1

        for i in range(768):
            temp = ktaTemp[i] * math.pow(2, ktaScale1)
            if temp < 0:
                self.kta[i] = int(temp - 0.5)
            else:
                self.kta[i] = int(temp + 0.5)
        self.ktaScale = ktaScale1

    def _ExtractKvPixelParameters(self):
        KvT = [0] * 4
        kvTemp = [0] * 768

        KvRoCo = (self.eeData[52] & 0xF000) >> 12
        if KvRoCo > 7:
            KvRoCo -= 16
        KvT[0] = KvRoCo

        KvReCo = (self.eeData[52] & 0x0F00) >> 8
        if KvReCo > 7:
            KvReCo -= 16
        KvT[2] = KvReCo

        KvRoCe = (self.eeData[52] & 0x00F0) >> 4
        if KvRoCe > 7:
            KvRoCe -= 16
        KvT[1] = KvRoCe

        KvReCe = self.eeData[52] & 0x000F
        if KvReCe > 7:
            KvReCe -= 16
        KvT[3] = KvReCe

        kvScale = (self.eeData[56] & 0x0F00) >> 8

        for i in range(24):
            for j in range(32):
                p = 32 * i + j
                split = 2 * (p // 32 - (p // 64) * 2) + p % 2
                kvTemp[p] = KvT[split]
                kvTemp[p] /= math.pow(2, kvScale)
                # kvTemp[p] = kvTemp[p] * mlx90640->offset[p];

        temp = abs(kvTemp[0])
        for kv in kvTemp:
            temp = max(temp, abs(kv))

        kvScale = 0
        while temp < 64:
            temp *= 2
            kvScale += 1

        for i in range(768):
            temp = kvTemp[i] * math.pow(2, kvScale)
            if temp < 0:
                self.kv[i] = int(temp - 0.5)
            else:
                self.kv[i] = int(temp + 0.5)
        self.kvScale = kvScale

    def _ExtractCILCParameters(self):
        ilChessC = [0] * 3

        self.calibrationModeEE = (self.eeData[10] & 0x0800) >> 4
        self.calibrationModeEE = self.calibrationModeEE ^ 0x80

        ilChessC[0] = self.eeData[53] & 0x003F
        if ilChessC[0] > 31:
            ilChessC[0] -= 64
        ilChessC[0] /= 16.0

        ilChessC[1] = (self.eeData[53] & 0x07C0) >> 6
        if ilChessC[1] > 15:
            ilChessC[1] -= 32
        ilChessC[1] /= 2.0

        ilChessC[2] = (self.eeData[53] & 0xF800) >> 11
        if ilChessC[2] > 15:
            ilChessC[2] -= 32
        ilChessC[2] /= 8.0

        self.ilChessC = ilChessC

    def _ExtractDeviatingPixels(self):
        # pylint: disable=too-many-branches
        pixCnt = 0

        while (
            (pixCnt < 768)
            and (len(self.brokenPixels) < 5)
            and (len(self.outlierPixels) < 5)
        ):
            if self.eeData[pixCnt + 64] == 0:
                self.brokenPixels.append(pixCnt)
            elif (self.eeData[pixCnt + 64] & 0x0001) != 0:
                self.outlierPixels.append(pixCnt)
            pixCnt += 1

        if len(self.brokenPixels) > 4:
            raise RuntimeError("More than 4 broken pixels")
        if len(self.outlierPixels) > 4:
            raise RuntimeError("More than 4 outlier pixels")
        if (len(self.brokenPixels) + len(self.outlierPixels)) > 4:
            raise RuntimeError("More than 4 faulty pixels")

        for brokenPixel1, brokenPixel2 in self._UniqueListPairs(self.brokenPixels):
            if self._ArePixelsAdjacent(brokenPixel1, brokenPixel2):
                raise RuntimeError("Adjacent broken pixels")

        for outlierPixel1, outlierPixel2 in self._UniqueListPairs(self.outlierPixels):
            if self._ArePixelsAdjacent(outlierPixel1, outlierPixel2):
                raise RuntimeError("Adjacent outlier pixels")

        for brokenPixel in self.brokenPixels:
            for outlierPixel in self.outlierPixels:
                if self._ArePixelsAdjacent(brokenPixel, outlierPixel):
                    raise RuntimeError("Adjacent broken and outlier pixels")

    def _UniqueListPairs(self, inputList):
        # pylint: disable=no-self-use
        for i, listValue1 in enumerate(inputList):
            for listValue2 in inputList[i + 1 :]:
                yield (listValue1, listValue2)

    def _ArePixelsAdjacent(self, pix1, pix2):
        # pylint: disable=no-self-use
        pixPosDif = pix1 - pix2

        if -34 < pixPosDif < -30:
            return True
        if -2 < pixPosDif < 2:
            return True
        if 30 < pixPosDif < 34:
            return True

        return False

    def _IsPixelBad(self, pixel):
        if pixel in self.brokenPixels or pixel in self.outlierPixels:
            return True

        return False

    def _I2CWriteWord(self, writeAddress, data):
        cmd = bytearray(4)
        cmd[0] = writeAddress >> 8
        cmd[1] = writeAddress & 0x00FF
        cmd[2] = data >> 8
        cmd[3] = data & 0x00FF
        dataCheck = [0]

        self.i2c_device.writeto(self.device_address, cmd)
        time.sleep(0.001)
        self._I2CReadWords(writeAddress, dataCheck)
        # if (dataCheck != data):
        #    return -2

    def _I2CReadWords(self, addr, buffer, *, end=None):
        gc.collect()
        if end is None:
            remainingWords = len(buffer)
        else:
            remainingWords = end
        offset = 0
        addrbuf = bytearray(2)

        while remainingWords:
            addrbuf[0] = addr >> 8  # MSB
            addrbuf[1] = addr & 0xFF  # LSB
            read_words = min(remainingWords, I2C_READ_LEN)
            self.i2c_device.readfrom_mem_into(self.device_address, addr, self.inbuf[0:read_words*2], addrsize=16)
            
            temp = read_words//10
            temps = [0]
            for i in range(9):
                temps.append(temps[i]+temp*2)


            for i in range(9):
                outwords = struct.unpack(
                    ">" + "H" * temp, self.inbuf[temps[i] : temps[i+1]]
                )
                
                for i, w in enumerate(outwords):
                    buffer[offset + i] = w
                offset += temp
                del outwords
            
            outwords = struct.unpack(
                ">" + "H" * (read_words-9*temp), self.inbuf[temps[9] : read_words*2]
            )
            for i, w in enumerate(outwords):
                buffer[offset + i] = w
            offset += (read_words-9*temp)
            del outwords
            
            remainingWords -= read_words
            addr += read_words

    def loop(self):
        global sensor_running
        
        while True:
#            stamp = time.ticks_ms()
            if sensor_running:
                try:
                    gc.collect()
                    self.getFrame()
                    gc.collect()
                except ValueError:
                    continue
#            time.sleep(0.01)
#            print("Gets one frame from sensor in %0.4f ms" % (time.ticks_diff(time.ticks_ms(), stamp)))        
            print("Sensor: Used RAM:", gc.mem_alloc(), "Remaining RAM:", gc.mem_free())

# End of driver code

if __name__=='__main__':

    """ Tests MLX90640 sensor: prints 32 x 24 temperatures"""

    # init sensor
    sensor = Sensor()
    sensor.refresh_rate = RefreshRate.REFRESH_2_HZ


    # View options
    PRINT_TEMPERATURES = False
    PRINT_COLORS = False
    PRINT_ASCIIART = False
    PRINT_DATA = True
    CYCLE = True
    TEST_LOOP = False
    
    WIDTH = 32
    HEIGHT = 24
    
    # test loop. Uncomment print statements in loop()
    sensor_running = TEST_LOOP
    if TEST_LOOP:
        sensor.loop()
    
    # Main loop
    while CYCLE:

        if PRINT_DATA:
            stamp = time.ticks_ms()
        try:
            gc.collect()
            sensor.getFrame(frame)
            gc.collect()
            print("MLX9060 sensor running")
        except ValueError:
            print("MLX9060 sensor error")
            continue

        if PRINT_DATA:
            print()
            print("Read 1 frame in %0.2f ms" % (time.ticks_ms() - stamp))
            print("Used RAM:", gc.mem_alloc(), "Remaining RAM:", gc.mem_free())
            print()

        if (PRINT_TEMPERATURES or PRINT_COLORS or PRINT_ASCIIART):
            for h in range(HEIGHT-1, -1, -1):
                for w in range(WIDTH):
                    temperature = round(frame[h * WIDTH + w], 2)
                    if PRINT_TEMPERATURES:
                        print("%0.1f" %temperature," ", end="")
                    color = int((temperature-20)/20*255)
                    if PRINT_COLORS:
                        print(color, " ", end="")
                    if PRINT_ASCIIART:
                        asciiart = "X"
                        if temperature < 20:
                            asciiart = " "
                        elif temperature < 23:
                            asciiart = "."
                        elif temperature < 25:
                            asciiart = "-"
                        elif temperature < 27:
                            asciiart = "*"
                        elif temperature < 29:
                            asciiart = "+"
                        elif temperature < 31:
                            asciiart = "x"
                        elif temperature < 33:
                            asciiart = "%"
                        elif temperature < 35:
                            asciiart = "#"
                        elif temperature < 37:
                            asciiart = "@"
                        elif temperature < 39:
                            asciiart = "&"
                        elif temperature < 41:
                            asciiart = "Z"
                        print(asciiart, end="")
                print()