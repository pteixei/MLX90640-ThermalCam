"""
`ILI9488 LCD / XPT2046 Touch`
================================================================================

Driver for the ILI9488 480 x 320 LCD / XPT2046 Touch


* Author(s): Waveshare

* with many changes to make it usable done by many people

Implementation Notes
--------------------

**Software and Dependencies:**


LCD Display / Resistive Touch Sensor
                    
TODO LIST:

    - New display functions (sleep/wake, rotation,...)

ERRORS:

"""

from machine import Pin, SPI, PWM
import framebuf
import time
import gc

# Hardware data

LCD_DC   = const(8)
LCD_CS   = const(9)
LCD_SCK  = const(10)
LCD_MOSI = const(11)
LCD_MISO = const(12)
LCD_BL   = const(13)
LCD_RST  = const(15)
TP_CS    = const(16)
TP_IRQ   = const(17)

TOUCH_SAMPLES = const(5)
CALIBRATION_LEVEL = const(1)

# LCD data

DISPLAY_WIDTH = const(480)
DISPLAY_HEIGHT = const(320)

# GUI data

# Adjustable data:
H_BLOCKS = const(5)         # Horizontal blocks that fill display
V_FIELDS = const(8)         # Vertical fields that fill display

# Fixed data:
BLOCK_STEP = const(DISPLAY_WIDTH // H_BLOCKS)
FIELD_STEP = const(DISPLAY_HEIGHT // V_FIELDS)

FRAME_BLOCK_WIDTH = const(BLOCK_STEP)
FRAME_BLOCK_HEIGHT = const(BLOCK_STEP)
FIELD_BLOCK_WIDTH = const(BLOCK_STEP)
FIELD_BLOCK_HEIGHT = const(FIELD_STEP)

FRAME_BLOCK_SIZE = const(FRAME_BLOCK_WIDTH * FRAME_BLOCK_HEIGHT)
FIELD_BLOCK_SIZE  = const(FIELD_BLOCK_WIDTH * FIELD_BLOCK_HEIGHT)

ICON_WIDTH = const(16)
ICON_SIZE = const(ICON_WIDTH * ICON_WIDTH)


# Framebuffers

frame_buffer = bytearray(FRAME_BLOCK_SIZE * 2)
field_buffer = bytearray(FIELD_BLOCK_SIZE * 2)

# classes

class Display(framebuf.FrameBuffer):
    # ILI9488 LCD/XPT2046 Touch driver
    def __init__(self, brightness=50):        
        
        self.current_buffer = frame_buffer
        self.icon_buffer = None
        
        self.cs = Pin(LCD_CS,Pin.OUT)
        self.rst = Pin(LCD_RST,Pin.OUT)
        self.dc = Pin(LCD_DC,Pin.OUT)
        
        self.tp_cs =Pin(TP_CS,Pin.OUT)
        self.irq = Pin(TP_IRQ,Pin.IN)

        self.irq.irq(trigger=Pin.IRQ_FALLING, handler=self.touch_interrupt_handler)
    
        # Touch data
        self.touch_active = False
        self.touch_coordinates = None
        self.touch_callback = None
        self.touch_point = None
        self.touch_samples = TOUCH_SAMPLES
        
        # Touch calibration points, flag and parameters
        self.in_operation = True
        self.screen_points = []
        self.touch_points = []
        self.calibration_points = 0
#        self.S_x, self.O_x, self.S_y, self.O_y = 0.2359818, -266.4914, -0.1642311, 441.7946
        self.S_x, self.O_x, self.S_y, self.O_y = 0.2409065, -294.2333, -0.1746017, 441.3569
#        self.S_x, self.O_x, self.S_y, self.O_y = 0.2202816, -239.4063, -0.1642866, 443.9218
        
        # Init SPI
        self.cs(1)
        self.dc(1)
        self.rst(1)
        self.tp_cs(1)
        self.spi = SPI(1,60_000_000,sck=Pin(LCD_SCK),mosi=Pin(LCD_MOSI),miso=Pin(LCD_MISO))

        print("ILI9488/XPT2046 detected on SPI")
        print("LCD ID:", self.get_ili9488_ID())
                
        super().__init__(frame_buffer, FRAME_BLOCK_WIDTH, FRAME_BLOCK_HEIGHT, framebuf.RGB565)
        
        self.init_display()
        self.brightness(brightness)

# start of core functions
    
    def write_cmd(self, cmd):
        self.cs(1)
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([cmd]))
        self.cs(1)

    def write_data(self, dat):
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(bytearray([dat]))
        self.cs(1)

    def read_data(self, num_bytes):
        self.cs(1)
        self.dc(1)
        self.cs(0)
        data = self.spi.read(num_bytes)
        self.cs(1)
        return data
    
    def get_ili9488_ID(self):
        """ Check Display ID """
        
        self.write_cmd(0x04)                          # RDID command to read ILI9488 ID
        time.sleep_ms(10)             
        
        # return ID read bytes
        return self.read_data(4) 
    
    def init_display(self):
        """Initialize ILI9488 display"""
        
        self.rst(1)
        time.sleep_ms(5)
        self.rst(0)
        time.sleep_ms(10)
        self.rst(1)
        time.sleep_ms(5)
        
        self.write_cmd(0x21)   #Display Inversion ON
        self.write_cmd(0xC2)   #Power Control 3
        self.write_data(0x33)  #Power Control 3 (DCA1, DCA0)
        self.write_cmd(0XC5)   #VCOM Control 1
        self.write_data(0x00)  #VCOM Control 1 (nVM)
        self.write_data(0x1E)  #VCOM Control 1 (VCM_REG) 
        self.write_data(0x80)  #VCOM Control 1 (VCM_REG_EN)
        self.write_cmd(0xB1)   #Frame Rate Control (In Normal Mode/Full Colors)
        self.write_data(0xB0)  #Frame Rate Control (In Normal Mode/Full Colors) (FRS, DIVA)
        self.write_cmd(0x36)   #Memory Access Control
        self.write_data(0x28)  #Memory Access Control (MY, MX, MV, ML, BGR, MH)
        self.write_cmd(0xE0)   #PGAMCTRL (Positive Gamma Control)
        self.write_data(0x00)  #PGAMCTRL (Positive Gamma Control, VP0) 
        self.write_data(0x13)  #PGAMCTRL (Positive Gamma Control, VP1)
        self.write_data(0x18)  #PGAMCTRL (Positive Gamma Control, VP2)
        self.write_data(0x04)  #PGAMCTRL (Positive Gamma Control, VP4)
        self.write_data(0x0F)  #PGAMCTRL (Positive Gamma Control, VP6)
        self.write_data(0x06)  #PGAMCTRL (Positive Gamma Control, VP13)
        self.write_data(0x3a)  #PGAMCTRL (Positive Gamma Control, VP20)
        self.write_data(0x56)  #PGAMCTRL (Positive Gamma Control, VP36, VP27)
        self.write_data(0x4d)  #PGAMCTRL (Positive Gamma Control, VP43)
        self.write_data(0x03)  #PGAMCTRL (Positive Gamma Control, VP50)
        self.write_data(0x0a)  #PGAMCTRL (Positive Gamma Control, VP57)
        self.write_data(0x06)  #PGAMCTRL (Positive Gamma Control, VP59)
        self.write_data(0x30)  #PGAMCTRL (Positive Gamma Control, VP61)
        self.write_data(0x3e)  #PGAMCTRL (Positive Gamma Control, VP62)
        self.write_data(0x0f)  #PGAMCTRL (Positive Gamma Control, VP63)
        self.write_cmd(0XE1)   #NGAMCTRL(Negative Gamma Control)
        self.write_data(0x00)  #NGAMCTRL(Negative Gamma Control, VN0)
        self.write_data(0x13)  #NGAMCTRL(Negative Gamma Control, VN1)
        self.write_data(0x18)  #NGAMCTRL(Negative Gamma Control, VN2)
        self.write_data(0x01)  #NGAMCTRL(Negative Gamma Control, VN4)
        self.write_data(0x11)  #NGAMCTRL(Negative Gamma Control, VN6)
        self.write_data(0x06)  #NGAMCTRL(Negative Gamma Control, VN13)
        self.write_data(0x38)  #NGAMCTRL(Negative Gamma Control, VN20)
        self.write_data(0x34)  #NGAMCTRL(Negative Gamma Control, VN27, VN36)
        self.write_data(0x4d)  #NGAMCTRL(Negative Gamma Control, VN43)
        self.write_data(0x06)  #NGAMCTRL(Negative Gamma Control, VN50)
        self.write_data(0x0d)  #NGAMCTRL(Negative Gamma Control, VN57)
        self.write_data(0x0b)  #NGAMCTRL(Negative Gamma Control, VN59)
        self.write_data(0x31)  #NGAMCTRL(Negative Gamma Control, VN61)
        self.write_data(0x37)  #NGAMCTRL(Negative Gamma Control, VN62)
        self.write_data(0x0f)  #NGAMCTRL(Negative Gamma Control, VN63)
        self.write_cmd(0X3A)   #Interface Pixel Format
        self.write_data(0x55)  #Interface Pixel Format (DPI, DBI)
        self.write_cmd(0x11)   #Sleep OUT
        
        time.sleep_ms(120)
        
        self.write_cmd(0x29)   #Display ON
        self.write_cmd(0xB6)   #Display Function Control
        self.write_data(0x00)  #Display Function Control (BYPASS, RCM, RM, DM, PTG, PT)
        self.write_data(0x62)  #Display Function Control (GS, SS, SM, ISC)
        self.write_cmd(0x36)   #Memory Access Control
        self.write_data(0x28)  #Memory Access Control (MY, MX, MV, ML, BGR, MH)

    def brightness(self,duty):
        """Sets the LCD brightness (0 to 100)"""

        pwm = PWM(Pin(LCD_BL))
        pwm.freq(1000)
        if(duty>=100):
            pwm.duty_u16(65535)
        else:
            pwm.duty_u16(655*duty)

# end of core functions

# start of graphic functions
    
    def clear_screen(self, color=0xffff):
        self.set_buffer()
        self.fill(color)
        for line in range(4):
            for column in range(5):
                self.set_block(column * BLOCK_STEP, line * BLOCK_STEP, BLOCK_STEP-1, BLOCK_STEP-1)
                self.show_block()

    def set_buffer(self, buffer_type='frame'):
        """change framebuffer (frame, bar, strip or button)"""

        if buffer_type == 'frame':
            self.current_buffer = frame_buffer
            width, height = FRAME_BLOCK_WIDTH, FRAME_BLOCK_HEIGHT
        elif buffer_type == 'icon':
            self.current_buffer = self.icon_buffer
            width, height = ICON_WIDTH, ICON_WIDTH
        else:
            self.current_buffer = field_buffer
            width, height = FIELD_BLOCK_WIDTH, FIELD_BLOCK_HEIGHT
        super().__init__(self.current_buffer, width, height, framebuf.RGB565)

    def set_block(self, x, y, dx, dy):
        """ sets the current display block """
        
        x1 , y1 = x+dx , y+dy
        
        # Column Address Set (SC,EC)
        self.write_cmd(0x2A)
        self.write_data(x>>8)    # Start Column (xH)
        self.write_data(x&0xff)  # Start Column (xL)
        self.write_data(x1>>8)    # End Column (x1H)
        self.write_data(x1&0xff)  # End Column (x1L)
        
        #Page Address Set (SP,EP)
        self.write_cmd(0x2B)
        self.write_data(y>>8)    # Start Page (yH)
        self.write_data(y&0xff)  # Start Page (yL)
        self.write_data(y1>>8)    # End Page (y1H)
        self.write_data(y1&0xff)  # End Page (y1L)
        
    def show_block(self):
        """ Shows the current block on LCD """
            
        self.write_cmd(0x2C)                              #Memory Write

        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(self.current_buffer)
        self.cs(1)        

    def draw_point(self,x,y,color):
        """Draws a point (a colored 4 pixel rectangle) on LCD"""

        bytearray_color =  bytearray([color&0xff, color>>8])

        self.write_cmd(0x2A)
        self.write_data((x-1)>>8)
        self.write_data((x-1)&0xff)
        self.write_data(x>>8)
        self.write_data(x&0xff)
        
        self.write_cmd(0x2B)
        self.write_data((y-1)>>8)
        self.write_data((y-1)&0xff)
        self.write_data(y>>8)
        self.write_data(y&0xff)
        
        self.write_cmd(0x2C)
        
        self.cs(1)
        self.dc(1)
        self.cs(0)
        for i in range(0,4):
            self.spi.write(bytearray_color)
        self.cs(1)

    def draw_pixel(self, x,y, pixel_size_x,pixel_size_y, color):
        """ Draws a pixel (a colored rectangle) on LCD """
              
        bytearray_color =  bytearray([color&0xff, color>>8])       
 
        self.write_cmd(0x2A)
        self.write_data(x>>8)
        self.write_data(x&0xff)
        self.write_data((x+pixel_size_x)>>8)
        self.write_data((x+pixel_size_x)&0xff)
        
        self.write_cmd(0x2B)
        self.write_data(y>>8)
        self.write_data(y&0xff)
        self.write_data((y+pixel_size_y)>>8)
        self.write_data((y+pixel_size_y)&0xff)
        
        self.write_cmd(0x2C)
        
        self.cs(1)
        self.dc(1)
        self.cs(0)
        for _i in range(0,pixel_size_x*pixel_size_y):
            self.spi.write(bytearray_color)
        self.cs(1)

    def load_block(self, path, w, h):
        """Load sprite image.

        Args:
            path (string): Image file path (bin file with RGB565 pyxels).
            w (int): Width of image.
            h (int): Height of image.
        Notes:
            w x h cannot exceed 3840
        """
        
        buf_size = w * h * 2
        if buf_size > FIELD_BLOCK_SIZE * 2:
            print("Sprite too big")
            return
        else:
            self.set_buffer('sprite')
            gc.collect()
            with open(path, "rb") as f:
                self.current_buffer = f.read(buf_size)

    def load_icon(self, path):
        """Load icon image.

        Args:
            path (string): Image file path (bin file with RGB565 pyxels).

        Notes:
            icon is a ICON_WIDTH x ICON_WIDTH sprite
        """
        gc.collect()
        with open(path, "rb") as f:
            self.icon_buffer = bytearray(f.read(ICON_SIZE * 2))
            
    def show_icon(self, filename, i, j):
        """Show icon at position i,j

        Args:
            i (int): i coordinate of image.
            j (int): j coordinate of image.
        Notes:
            icon must have been loaded in icon_buffer
        """
        self.load_icon(filename)
        
        if self.icon_buffer is not None:
            self.set_buffer('icon')
            self.set_block(i, j, ICON_WIDTH-1, ICON_WIDTH)
            self.show_block()

    def show_sprite_block(self, i, j, w, h):
        """Load and show sprite image.

        Args:
            i (int): i coordinate of image.
            j (int): j coordinate of image.
            w (int): Width of image.
            h (int): Height of image.
        Notes:
            sprite must have been loaded in field_buffer
        """
                
        if self.current_buffer is not None:
            self.set_block(i, j, w, h)
            self.show_block()


#     def normalize_coordinates(self, x, y):
#         """Normalize mean X,Y values to match LCD screen."""
#          
#         x = int(self.x_multiplier * x + self.x_add)
#         y = int(self.y_multiplier * y + self.y_add)
#  
#         return y, 320 - x

#    def get_touch(self):
# Uncomment bellow to use interrupts:       
    def touch_interrupt_handler(self, pin):
        """Read touch coordinates and blocks until touch reset"""

        if self.irq.value() == 0 and not self.touch_active:  # Trigger only if no active touch

            # Switch SPI settings for the touch sensor
            original_spi = self.spi
            self.spi = SPI(1, 5_000_000, sck=Pin(LCD_SCK), mosi=Pin(LCD_MOSI), miso=Pin(LCD_MISO))
            self.tp_cs(0)
                
            i_point = 0
            j_point = 0
                    
            # average readings
            for _ in range(self.touch_samples):
                
                self.spi.write(bytearray([0XD0]))
                data = self.spi.read(2)
                time.sleep_us(10)  # 10 us
                i_point += (((data[0]<<8)+data[1])>>3)
                
                self.spi.write(bytearray([0X90]))
                data = self.spi.read(2)
                j_point += (((data[0]<<8)+data[1])>>3)
            
#                time.sleep(0.001)  # 1 ms

            i_point = i_point//self.touch_samples
            j_point = j_point//self.touch_samples
            
            # Note: Touch and screen coordinates need a couple of rotations: xs = yt; ys = k - xt)
            # touch_point corrects the rotations but 
            self.touch_point = (j_point, i_point)
            
            # Switch back SPI settings to LCD
            self.tp_cs(1) 
            self.spi = original_spi

            # convert to LCD (480x320) coordinates and store the touch coordinates 
#            x, y = self.normalize_coordinates(i_point, j_point)
            x, y = self.map_coordinates(self.touch_point)
            self.touch_coordinates = (max(0, min(x, 479)), max(0, min(y, 319)))      # touch/screen coordinates
            self.touch_active = True                                                 # Mark touch as active


            time.sleep(0.3)  # 300 ms
  
            # callback
            if self.touch_callback is not None:
                self.touch_callback(self.touch_coordinates, self.in_operation)    #callback must input coordinates and mode
                if self.in_operation:
                    self.touch_active = False                                     # Mark touch as inactive after callback
                    
                     
    def set_touch(self, callback):
        """ set touch calback """
        self.touch_callback = callback

    def reset_touch(self):
        """ resets and unblocks touch """
        self.touch_coordinates = None
        self.touch_active = False

    def calibrate_touch(self, level=CALIBRATION_LEVEL):
        """
            Minimum squares algorithm to calibrate the touch reader to the LCD screen
                A set of screen points are generated (level dependent)
                A set of touch readings are done (touch must be put in calibration mode (more retries)
                S_x, O_x, S_y, O_y parameters are calculated
            
                A mapping method allows calibrated conversion from touch to screen coordinates        

    """
        self.in_operation = False
        self.get_screen_points(level)
        if self.get_touch_points():
            self.calculate_calabration_parameters()
        self.touch_samples = TOUCH_SAMPLES
        self.in_operation = True
        
    def calculate_calabration_parameters(self):
        """

            calculate S_x, O_x, S_y, O_y parameters for touch to screen mapping
                expects 2 lists (self.touch_points, self.screen_points) with same size    
        """

        # Mean calculation         
        n = len(self.touch_points)
        if n != self.calibration_points:
            print(f"Touch points number ({n}) must match screen point number ({self.calibration_points})")
            return None
        
        mean_x = mean_y = mean_xs = mean_ys = 0
        for (x, y), (xs, ys) in zip(self.touch_points, self.screen_points):
            mean_x += x
            mean_y += y
            mean_xs += xs
            mean_ys += ys

        mean_x /= n
        mean_y /= n
        mean_xs /= n
        mean_ys /= n

        #S_x, O_x, S_y e O_y calculation
        numerator_x = denominator_x = numerator_y = denominator_y = 0
        for (x, y), (xs, ys) in zip(self.touch_points, self.screen_points):
            numerator_x += (x - mean_x) * (xs - mean_xs)
            denominator_x += (x - mean_x) ** 2
            numerator_y += (y - mean_y) * (ys - mean_ys)
            denominator_y += (y - mean_y) ** 2
            
        self.S_x = numerator_x / denominator_x
        self.O_x = mean_xs - self.S_x * mean_x
        self.S_y = numerator_y / denominator_y
        self.O_y = mean_ys - self.S_y * mean_y
    
        return self.S_x, self.O_x, self.S_y, self.O_y

    def map_coordinates(self, touch_point):
        """ maps touch readings into calibrated screen point """

        (x, y) = touch_point 
        xs = int(self.S_x * x + self.O_x)
        ys = int(self.S_y * y + self.O_y)
        return xs, ys

    def get_screen_points(self, level=CALIBRATION_LEVEL):    
        """
            get regularly distributed screen point for touch reading
            
                 - level values define the density of an exponential spider-web of evenly scatered points
                 - level: 0 -> 1 pt; 1 -> 5 pt; 2 -> 9 pt; 3 -> 25 pt; ...
        """

        self.calibration_points = 0
        self.screen_points = []
                
        mid_i = DISPLAY_WIDTH // 2
        mid_j = DISPLAY_HEIGHT // 2
        points = 2 ** level

        delta_i = DISPLAY_WIDTH // points
        delta_j = DISPLAY_HEIGHT // points
        
        for point in range(points + 1):
            
            i = point * delta_i

            # 3 horizontal lines
            j = 0
            self.screen_points.append((i, j))
            j = mid_j
            self.screen_points.append((i, j))
            j = DISPLAY_HEIGHT
            self.screen_points.append((i, j))
            
            self.calibration_points += 3
            
            j = point * delta_j
            
            if j > 0 and j != mid_j and j < DISPLAY_HEIGHT:
                
                # 2 diagonal lines
                self.screen_points.append((i, j))
                self.screen_points.append((i, DISPLAY_HEIGHT - j))
                
                # 3 vertical lines
                i = 0
                self.screen_points.append((i, j))
                i = mid_i
                self.screen_points.append((i, j))
                i = DISPLAY_WIDTH
                self.screen_points.append((i, j))
            
                self.calibration_points += 5
                
    def get_touch_points(self, timeout=20):
        """
            Get touch readings for each screen point
                for all screen points
                   plot (clear screen, render screen pixels)
                   get touch (collect coordinates)
                   plot (render touch pixels)
                   save list in self.touch_points[]
        """

        def clip(x,y):
            if x < 4:
                x1 = 0
            elif x > DISPLAY_WIDTH - 4:
                x1 = DISPLAY_WIDTH - 7
            else:
                x1 = x
            if y < 4:
                y1 = 0
            elif y > DISPLAY_HEIGHT - 4:
                y1 = DISPLAY_HEIGHT - 7
            else:
                y1 = y
            return x1, y1
        
        self.touch_points = []
        
        for point in self.screen_points:
            (x,y) = point
            x1, y1 = clip(x,y)
            
            self.draw_pixel(x1, y1, 8, 8, 0x9c5c)         # plot a blue spot
            
            start_time = time.time()

            while True:
                if (time.time() - start_time) >= timeout:
                    return False
                if self.touch_active:                            # wait for a valid touch
                    break
            
            self.touch_points.append(self.touch_point)
            self.draw_pixel(x1, y1, 8, 8, 0x07E0)       # plot a red spot
            self.touch_active = False                            # reset touch
        
        return True
                
# end of graphic functions

# End of driver code



if __name__=='__main__':
    
    """
        Tests ILI9488 LCD:
            renders dummy windows
                Frame (32 x 24 color matrix)
                Bar (Text, Icons)
                Strip (color scale)
            
        Tests XPT2046 Touch:
            tests touch readouts
                interrupt callback
                calibration
            
    """
    
    # Base colors

    RED    =   const(0x07E0)
    GREEN  =   const(0x001f)
    #BLUE   =   const(0xf800)
    BLUE   =   const(0x9c5c)
    CYAN   =   const(0x07ff)
    YELLOW =   const(0xffe0)
    WHITE  =   const(0xffff)
    BLACK  =   const(0x0000)
    GRAY   =   const(0xbdf7)
    
    # init display
    LCD = Display()
    
#     print("Display: Used RAM:", gc.mem_alloc(), "Remaining RAM:", gc.mem_free())

    # Test flags
    frame_visible = False
    bar_and_strip_visible = False
    read_touch = False
    sprite = False
    icon = False
    calibrate = True
    
    # Draw Frame 
    if frame_visible:        
        stamp = time.ticks_ms()
        for j in range(0,24):
            for i in range(0,32):
                color = ((i+1) * (j+2))*90
                LCD.draw_pixel(i*12, j*12, 12, 12, color)
        print("Render frame in %0.4f ms" % (time.ticks_diff(time.ticks_ms(), stamp)))        
    
    # Draw bar & strip
    if bar_and_strip_visible:    
        LCD.set_buffer('bar')   # BAR
        for j in range(8):
            LCD.set_block(384,(40*j),96,40)
            LCD.fill(WHITE)
            if j < 6:
                LCD.text("Bar: "+str(j), 10,12, RED)
            LCD.show_block()
            
        for i in range(4):      # STRIP
            LCD.set_block(96*i,288,96-1,40)
            LCD.fill(BLUE)
            LCD.text("Strip: "+str(i), 10,12, WHITE)
            LCD.show_block()
        
        if icon:                # ICON (16x16)
            LCD.show_icon("up.bin", 426,252)
            LCD.show_icon("down.bin", 426,294)                
            LCD.show_icon("left.bin", 392,272)
            LCD.show_icon("right.bin", 456,272)
            LCD.show_icon("ok.bin", 426,273)

    if sprite:        # Pictures and symbols (field sized)
        """
        Files available: "button_bottom565",
                        "button_left_bottom565",
                        "button_left_top565",
                        "button_right_bottom565",
                        "button_right_top565",
                        "button_top565",
                        "button_full_ok_bottom565",
                        "button_full_ok_top565"
        """
        filename = "button_full_ok_top565.bin"
        LCD.load_block(filename, 95,40)
        LCD.show_sprite_block(383,240,95,40)

        filename = "button_full_ok_bottom565.bin"
        LCD.load_block(filename, 95,40)
        LCD.show_sprite_block(383,279,95,40)
    
    # Test Touch Calibration
    if calibrate:
        LCD.clear_screen()
        LCD.calibrate_touch(3)
        
        print("S_x, O_x, S_y, O_y parameters: ", LCD.S_x, LCD.O_x, LCD.S_y, LCD.O_y)
        
        print("Screen Points: ", LCD.screen_points)
        print("Touch Points: ", LCD.touch_points)
        
        # loop to read touch and plot the converted coordinates
        while True:
            if LCD.touch_active:                            # wait for a valid touch point
                xs, ys = LCD.map_coordinates(LCD.touch_point)
                
                print("Screen Point: ", xs, ys)
                print("Touch Point: ", LCD.touch_point)
                
                LCD.draw_pixel(xs, ys, 8, 8, GREEN)       # plot a green spot

                LCD.touch_active = False

            
    # Test Touch
    class TestCallback():
        def __init__(self):
            self.coordinates = (0,0)
        def show(self, touch_coordinates):
            self.coordinates = touch_coordinates
            print("Touch coordinates: ", touch_coordinates)
            (i,j) = touch_coordinates

        def touch_coordinates(self):
            coordinates = self.coordinates
            self.coordinates = None
            return coordinates
    
    if read_touch:
        
        test_callback = TestCallback()    
        LCD.set_touch(test_callback.show)
    
        while True:

    #        print("Display: Used RAM:", gc.mem_alloc(), "Remaining RAM:", gc.mem_free())
                
            coordinates = test_callback.touch_coordinates()
            
            if coordinates is not None:
                (X_Point,Y_Point) = coordinates
                
                # check if touch area is aceptable
                if X_Point > 384:
                    touched_field = Y_Point // 40
                    touched_zone = (X_Point-384) // 32
                    
                    print(touched_field, " - field touched", touched_zone, " - zone touched")
                    
                time.sleep_ms(500)
                gc.collect()
