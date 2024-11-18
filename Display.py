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

from machine import Pin,SPI,PWM
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
TOUCH_SAMPLES = 3

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

# Base colors

RED    =   const(0x07E0)
GREEN  =   const(0x001f)
BLUE   =   const(0xf800)
CYAN   =   const(0x07ff)
YELLOW =   const(0xffe0)
WHITE  =   const(0xffff)
BLACK  =   const(0x0000)
GRAY   =   const(0xbdf7)

# Framebuffers

frame_buffer = bytearray(FRAME_BLOCK_SIZE * 2)
field_buffer = bytearray(FIELD_BLOCK_SIZE * 2)

# classes

class Display(framebuf.FrameBuffer):
    # ILI9488 LCD/XPT2046 Touch driver
    def __init__(self, brightness=50):        
        
        self.current_buffer = frame_buffer
        
        self.cs = Pin(LCD_CS,Pin.OUT)
        self.rst = Pin(LCD_RST,Pin.OUT)
        self.dc = Pin(LCD_DC,Pin.OUT)
        
        self.tp_cs =Pin(TP_CS,Pin.OUT)
        self.irq = Pin(TP_IRQ,Pin.IN)

# Uncomment bellow to use interrupts:
        self.irq.irq(trigger=Pin.IRQ_FALLING, handler=self.touch_interrupt_handler)
    
        # Variable to store touch coordinates
        self.touch_coordinates = None
        self.touch_active = False
        
        # Touch calibration values   (attention: x/y is switched in the touch device     
        self.x_max, self.x_min = 2700, 1000
        self.y_max, self.y_min = 3200, 1200

        self.x_multiplier = DISPLAY_HEIGHT / (self.x_max - self.x_min)
        self.x_add = self.x_min * -self.x_multiplier
        self.y_multiplier =  DISPLAY_WIDTH / (self.y_max - self.y_min)
        self.y_add = self.y_min * -self.y_multiplier
        
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

    def set_buffer(self, buffer_type='frame'):
        """change framebuffer (frame, bar or strip bufers)"""
        
        if buffer_type == 'frame':
            self.current_buffer = frame_buffer
            width, height = FRAME_BLOCK_WIDTH, FRAME_BLOCK_HEIGHT
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

    def normalize_coordinates(self, x, y):
        """Normalize mean X,Y values to match LCD screen."""
         
        x = int(self.x_multiplier * x + self.x_add)
        y = int(self.y_multiplier * y + self.y_add)
 
        return y, 320 - x

#    def get_touch(self):
# Uncomment bellow to use interrupts:       
    def touch_interrupt_handler(self, pin):
        """Read touch coordinates."""

        if self.irq.value() == 0 and not self.touch_active:  # Trigger only if no active touch

            # Switch SPI settings for the touch sensor
            original_spi = self.spi
            self.spi = SPI(1, 5_000_000, sck=Pin(LCD_SCK), mosi=Pin(LCD_MOSI), miso=Pin(LCD_MISO))
            self.tp_cs(0)
                
            i_point = 0
            j_point = 0
                    
            # average readings
            for _ in range(TOUCH_SAMPLES):
                
                self.spi.write(bytearray([0XD0]))
                data = self.spi.read(2)
                time.sleep_us(10)
                i_point += (((data[0]<<8)+data[1])>>3)
                
                self.spi.write(bytearray([0X90]))
                data = self.spi.read(2)
                j_point += (((data[0]<<8)+data[1])>>3)

            i_point = i_point//TOUCH_SAMPLES
            j_point = j_point//TOUCH_SAMPLES
            
            # Switch back SPI settings to LCD
            self.tp_cs(1) 
            self.spi = original_spi

            # convert to LCD (480x320) coordinates and store the touch coordinates 
            x,y = self.normalize_coordinates(i_point, j_point)
            
            self.touch_coordinates = (max(0, min(x, 479)), max(0, min(y, 319)))      # clips coordinates
            self.touch_active = True                                                 # Mark touch as active

                
# end of graphic functions

# End of driver code



if __name__=='__main__':
    
    """ Tests ILI9488 LCD: prints Frame (32 x 24 color matrix), Bar (Text, Icons), Strip (color scale)"""

    # init display
    LCD = Display()

#     print("Display: Used RAM:", gc.mem_alloc(), "Remaining RAM:", gc.mem_free())

    # Window flags
    frame_visible = True
    bar_and_strip_visible = True
    read_touch = True
    
    # Draw Frame 
    if frame_visible:        
        stamp = time.ticks_ms()
        for j in range(0,24):
            for i in range(0,32):
                color = ((i+1) * (j+2))*90
                LCD.draw_pixel(i*12, j*12, 12, 12, color)
        print("Render frame in %0.4f ms" % (time.ticks_diff(time.ticks_ms(), stamp)))        
    
    # test bar & strip blocks
    if bar_and_strip_visible:    
        LCD.set_buffer('bar')
        for j in range(8):
            LCD.set_block(384,(40*j),96,40)
            LCD.fill(WHITE)
            LCD.text("Bar: "+str(j), 10,12, RED)
            LCD.show_block()
        for i in range(4):
            LCD.set_block(96*i,288,96-1,40)
            LCD.fill(BLUE)
            LCD.text("Strip: "+str(i), 10,12, WHITE)
            LCD.show_block()            
    
    # Test Touch
    while read_touch:

        print("Display: Used RAM:", gc.mem_alloc(), "Remaining RAM:", gc.mem_free())

# Uncomment bellow to use interrupts:           
#         LCD.get_touch()
        
        if LCD.touch_coordinates is not None:
            [X_Point,Y_Point] = LCD.touch_coordinates            
            
            print(LCD.touch_coordinates)
            
            # check if touch area is aceptable
            if X_Point > 384:
                touched_field = Y_Point // 40
                touched_zone = (X_Point-384) // 32
                
                print(touched_field, " - field touched", touched_zone, " - zone touched")
                
            time.sleep_ms(100)
            
            # Reset the touch_active flag and coordinates after processing
            LCD.touch_active = False
            LCD.touch_coordinates = None
        gc.collect()
