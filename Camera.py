"""
Thermal camera
================================================================================

Thermal Camera dual threaded software:
- 32x24 temperature matrix acquisition from MLX90640 sensor
- ILI9488 touch display 420x320 for user interface
- "orchestrator"  


* Author(s): Paulo Teixeira


Implementation Notes
--------------------

**Software and Dependencies:**

TODO LIST:

- optimize performance:
    - loops need some tuneup

- create a method to manage configs:
    - aggregate all configs into coeherent dataset (storable in flash)

- create a method to manage status and content:
    - create dict with keys: name, status, values, types, data, positions, colors,... organized into pages, lines, columns
    - aggregate data from all sources (statistics, configs, pico, status)
    - encode mode (show/read), x/y position, navigation (next element)
    - sets a state-machine in main loop for navigation and function runing ( eg, save pic to flash, change mode, etc..)

- Create Systems class with:
    - SD card read/write/list
    - Pico Temperature and Voltage
    - Pico RTC
    - Leds and Buttons
    - Beep
    - Accelerometer/Rotation
    - Sleep/Wake/Shutdown
    
    - Use those methods in Windows
    
ERRORS:

"""

from Context import content
from Sensor import Sensor, RefreshRate, frame, running
from Windows import Screen, Payload, Configs
import _thread
import time
import gc

Payload.frame = frame                    
Payload.content = content
Payload.configs = Configs()

def core1_thread():
    """ Core 1: GUI and Navigation
        - GUI: display (ILI9488) driver and graphic tools
            - main loop, status,
                options (menu, views, values)
                actions (frame, bar, configs, warnings, storage)
    """
    def StartupData():
        global Payload
        conf = Payload.configs
        conf.minimum_temperature = 25
        conf.maximum_temperature = 35
        conf.interpolate_pixels = False
        conf.calculate_colors = False
        conf.max_min_set = True
        
    # Core 1 starts here
    
    # initialize settings 
    StartupData()
    
    # launch screen
    screen = Screen()

    # run screen
    screen.loop(running)

   # Core 1 ends here

def core0_thread():
    """ Core 0: Sensor and System
        - Sensor: sensor (MLX9060) driver
        - System: system control and monitoring, SD card, leds, buttons
    """
    # Core 0 starts here
    global Payload
    
   # launch sensor
    sensor = Sensor()
    
    if Payload.configs.interpolate_pixels:
        sensor.refresh_rate = RefreshRate.REFRESH_0_5_HZ
    else:    
        sensor.refresh_rate = RefreshRate.REFRESH_2_HZ

    # run sensor
    sensor.loop(running)
    
    # Core 0 ends here


# Main
running = True
second_thread = _thread.start_new_thread(core1_thread, ())
time.sleep_ms(10)
core0_thread()
running = False
# Main ends here
