"""
`ILI9488 LCD/XPT2046 Touch`
================================================================================

Driver for the ILI9488 480 x 320 LCD / XPT2046 Touch


* Author(s): Waveshare

* with many changes to make it usable done by many people

Implementation Notes
--------------------

**Software and Dependencies:**


LCD Display
    
    - Block is a display area that can be used in mosaics
        - 3 type of block (3 types of frambuf):
        - Block: block_buffer:
            - frame_buffer (96x96)used in frame: (384x288) 
                - 4 x 3 blocks mosaic is needed for ploting frame pixels from sensor
                - touch reading can occur for pointing position to get temperature
            - bar_buffer (96x48) used in bar: (192x320) 
                - 5 x 6 (rightmost) for text and icons
                - 5 columns and 6 lines (fields)
                - touch reading can occur for pointing navigation, value setting and picking
            - strip_buffer (192 x 32) user in Strip block(384x32):
                - 2 block (bottom) for pixels (temperature color scale), text and icons
                - touch reading can occur for pointing navigation, value setting and picking
                
    - Window is a group of blocks
    
    - Screen is organized into 3 Windows:       
        - Frame window: 4 x 3 blocks at the left side of the screen
        - Bar window: 5 x 6 blocks at the right side of the screen
        - Strip Window: 2 x 1 blocks in lower part of frame blocks
        
        - Frame and Bar may overlap , needing to implement a focus mechanism
        
        - blocks used in frame window have pixels and text
        - blocks used in bar windows have text and icons
        - blocks used in strip windows have pixels and text
        

TODO LIST:

    - New display functions (sleep/wake, rotation,...)

    - New buffer/block types
        - for fields in Bar (96 x 48 = 4608) 
        - for strip (192 x 32 = 6144)
        - Standard blocks (96x96 = 9216) only used in frame
    - change:
        - Bar Render, set_buffer(in Display)
            - Make Bar_render parser more generic and efficient (interpret list of graphical and data source primitives)
            - Make multi-column Bar renderer.

        - Strip Render
            - Make Sstrip Render multi-block
            - Print Min/Max temperatures in scale
        - Frame Render
            - Improve performance
            - Print cursor and spot temperature in frame    


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

# GUI data
DISPLAY_WIDTH = const(480)
DISPLAY_HEIGHT = const(320)

BLOCK_STEP = const(96)
FIELD_STEP = const(48)
STRIP_STEP = const(32)

FRAME_BLOCK_WIDTH = const(BLOCK_STEP)
FRAME_BLOCK_HEIGHT = const(BLOCK_STEP)
BAR_BLOCK_WIDTH = const(BLOCK_STEP)
BAR_BLOCK_HEIGHT = const(FIELD_STEP)
STRIP_BLOCK_WIDTH = const(2 * BLOCK_STEP)
STRIP_BLOCK_HEIGHT = const(STRIP_STEP)

FRAME_BLOCK_SIZE = const(FRAME_BLOCK_WIDTH * FRAME_BLOCK_HEIGHT)
STRIP_BLOCK_SIZE  = const(STRIP_BLOCK_WIDTH * STRIP_BLOCK_HEIGHT)
BAR_BLOCK_SIZE  = const(BAR_BLOCK_WIDTH * BAR_BLOCK_HEIGHT)

# Base colors
RED    =   const(0x07E0)
GREEN  =   const(0x001f)
BLUE   =   const(0xf800)
CYAN   =   const(0x07ff)
YELLOW =   const(0xffe0)
WHITE  =   const(0xffff)
BLACK  =   const(0x0000)
GRAY   =   const(0xd69a)


# Buffer framebuffer
# block_buffer = bytearray(BLOCK_SIZE*2)
# block_s_buffer =  bytearray(STRIP_SIZE*2)
frame_buffer = bytearray(FRAME_BLOCK_SIZE * 2)
strip_buffer =  bytearray(STRIP_BLOCK_SIZE * 2)
bar_buffer = bytearray(BAR_BLOCK_SIZE * 2)

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
        
        self.cs(1)
        self.dc(1)
        self.rst(1)
        self.tp_cs(1)
        self.spi = SPI(1,60_000_000,sck=Pin(LCD_SCK),mosi=Pin(LCD_MOSI),miso=Pin(LCD_MISO))

        print("ILI9488 detected on SPI")
        print("LCD ID:", self.get_ili9488_ID())
                
        super().__init__(self.current_buffer, FRAME_BLOCK_WIDTH, FRAME_BLOCK_HEIGHT, framebuf.RGB565)
        
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
        # Check Display ID
        self.write_cmd(0x04)       # Comando RDID para ler o identificador do ILI9488
        time.sleep_ms(10)             # Pequeno atraso para garantir a resposta
        
        # return 3 ID read bytes
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
            super().__init__(self.current_buffer, FRAME_BLOCK_WIDTH, FRAME_BLOCK_HEIGHT, framebuf.RGB565)
        elif buffer_type == 'bar':
            self.current_buffer = bar_buffer
            super().__init__(self.current_buffer, BAR_BLOCK_WIDTH, BAR_BLOCK_HEIGHT, framebuf.RGB565)
        elif buffer_type == 'strip':
            self.current_buffer = strip_buffer
            super().__init__(self.current_buffer, STRIP_BLOCK_WIDTH, STRIP_BLOCK_HEIGHT, framebuf.RGB565)

    def set_block(self, x, y, dx, dy):
        """sets the current window"""
        
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
        """Shows the current window"""
            
        self.write_cmd(0x2C)   #Memory Write

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

    def draw_pixel(self,x,y,pixel_size_x,pixel_size_y,color):
        """Draws a pixel (a colored rectangle) on LCD"""
              
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

    def get_touch(self):
        """Gets touched X/Y"""
        
        if self.irq() == 0:
            # change SPI settings to Touch sensor
            self.spi = SPI(1,5_000_000,sck=Pin(LCD_SCK),mosi=Pin(LCD_MOSI),miso=Pin(LCD_MISO))
            self.tp_cs(0)
            
            i_point = 0
            j_point = 0
            
            # average readings
            for i in range(0,3):
                self.spi.write(bytearray([0XD0]))
                Read_date = self.spi.read(2)
                time.sleep_us(10)
                i_point += (((Read_date[0]<<8)+Read_date[1])>>3)
                
                self.spi.write(bytearray([0X90]))
                Read_date = self.spi.read(2)
                j_point += (((Read_date[0]<<8)+Read_date[1])>>3)

            i_point=i_point/3
            j_point=j_point/3
            
            # change back SPI settings to LCD
            self.tp_cs(1) 
            self.spi = SPI(1,60_000_000,sck=Pin(LCD_SCK),mosi=Pin(LCD_MOSI),miso=Pin(LCD_MISO))

            # convert to LCD (480x320) coordinates
            X_Point = int((j_point-430)*480/3270)
            Y_Point = 320-int((i_point-430)*320/3270)
            # and clean them
            X_Point = max(0, min(X_Point, 479))
            Y_Point = max(0, min(Y_Point, 319))
            return ([X_Point,Y_Point])
                
# end of graphic functions

# End of driver code



if __name__=='__main__':
    
    """ Tests ILI9488 LCD: prints Frame (32 x 24 color matrix), Bar (Text, Icons), Strip (color scale)"""

    # init display
    LCD = Display()

    # Window flags
    frame_visible = True
    read_touch = False
    
    # Draw Frame
    if frame_visible:        
        stamp = time.ticks_ms()
        for j in range(0,24):
            for i in range(0,32):
                color = (i * j)*90
                LCD.draw_pixel(i*12, j*12, 12, 12, color)
                
        print("Render frame in %0.4f ms" % (time.ticks_diff(time.ticks_ms(), stamp)))        
        for j in range(0,3):
            LCD.set_block(384,(96*j),96,97)
            LCD.fill(WHITE)
            LCD.text("Text: "+str(j), 10,20, RED)
            LCD.show_block()
        
    
    # Test Touch        
    while read_touch:
        touch_point = LCD.get_touch()
        if touch_point != None:
            [X_Point,Y_Point] = touch_point            
            # check if touch area is aceptable
            if X_Point > 288:
                touched_field = Y_Point // 48
                print(touched_field, "- field touched")
                time.sleep_ms(50)
