"""
 Graphic User Interface for Thermal Cam based on
 Raspberry pi Pico, MLX90640 IR sensor, ILI9488/XPT2046 Touch LCD 
================================================================================


* Author(s): Paulo Teixeira


Implementation Notes
--------------------

**Software and Dependencies:**


Screen is a simple GUI class that creates, organizes and renders windows for the MLX90640 Thermal Camera.
Screen depends on Display and is structured around:
    
    - Block: a display area that can be used in mosaics to form windows. Blocks need framebuffers
        
    - Window: a group of blocks that shows content and read user input (touched objects in screen)
    
    - Screen: a group of Windows:       
        - Frame window: 4 x 3 frame blocks at the left side of the screen (block buffer - show pixels and text)
        - Bar window: 1-5 x 5 bar blocks at the right side of the screen (bar buffer - show pictures (Icons) and text)
        - Strip Window: 2 strip_block at bottom side of the screen  (strip buffer - show pixels and text)
        
        - Frame and Bar may overlap , needing to implement a focus mechanism
        
        - frame window blocks use frame_buffer and show text and pixels
        - bar window blocks use field_buffer and show text and icons
        - strip window blocks use field_buffer and show pixels and text
          
        - Screen is managed by WindowsManager
        - User input is managed by InputHandler
TODOS:
    - Remake Bar renderer!
        - Make Bar_render parser more generic and efficient (interpret list of graphical and data source primitives)

    - Complete Strip with modes, auto min/max and temperature labels
    - Complete Frame with zoom, cursor and temperature labels
        - Frame Render
            - Improve performance
            - Print cursor and spot temperature in frame    

    - Make InputHandler logic (status, content page navigation, user inputs, actions)
    
ERRORS:

"""
from Display import Display, DISPLAY_WIDTH, DISPLAY_HEIGHT, BLOCK_STEP, FIELD_STEP
from Sensor import lock, running, frame
from Data import Payload
import time
import gc

# core data
SOURCE_SIZE = const(768)

# Interpolation data Kernels
#Sigma=1
P00 = const(0.077847)
P01 = const(0.201164)            #0.123317+0.077847
P02 = const(0.519827)            #0.195346+0.123317+0.123317+0.077847
#Sigma=0.5
#P00 = const(0.024879)
#P01 = const(0.132852)            #0.107973+0.024879
#P02 = const(0.709417)            #0.468592+0.107973+0.107973+0.024879
#Sigma=2
#P00 = const(0.102059)
#P01 = const(0.217408)            #0.115349+0.102059
#P02 = const(0.463128)            #0.130371+0.115349+0.115349+0.102059

Interpolation_offsets = ((-65, -64 , -1, 0),
                         (-64, -63, 0, 1),
                         (-1, 0, 64, 65),
                         (0, 1, 64, 65))

Kernel = ((P00, P01, P01, P02),                            #Sigma index 1                
          (P01, P00, P02, P01),
          (P01, P02, P00, P01),
          (P02, P01, P01, P00))

# GUI data

# Adjustable data:
FRAME_STEP = const(96)      # Frame block "real" step
COLUMNS = const(1)

TEXT_STEP = FIELD_STEP // 2
ZONE_STEP = BLOCK_STEP // 3

FRAME_BLOCK_WIDTH = FRAME_STEP
FRAME_BLOCK_HEIGHT = FRAME_STEP
FIELD_BLOCK_WIDTH = BLOCK_STEP
FIELD_BLOCK_HEIGHT = FIELD_STEP

FRAME_WINDOW_WIDTH = 4 * FRAME_BLOCK_WIDTH
FRAME_WINDOW_HEIGHT = 3 * FRAME_BLOCK_HEIGHT
BAR_WINDOW_WIDTH = COLUMNS * FIELD_BLOCK_WIDTH
BAR_WINDOW_HEIGHT = 8 * FIELD_BLOCK_HEIGHT
STRIP_WINDOW_WIDTH = 4 * FIELD_BLOCK_WIDTH
STRIP_WINDOW_HEIGHT = FIELD_BLOCK_HEIGHT

Window_shapes = {
            'frame':
                {'size': (FRAME_WINDOW_WIDTH, FRAME_WINDOW_HEIGHT),
                 'place':(0, 0)},
            'bar':
                {'size': (BAR_WINDOW_WIDTH, BAR_WINDOW_HEIGHT),
                 'place':(DISPLAY_WIDTH - BAR_WINDOW_WIDTH, 0)},
            'strip':
                {'size': (STRIP_WINDOW_WIDTH, STRIP_WINDOW_HEIGHT),
                 'place':(0, DISPLAY_HEIGHT - STRIP_WINDOW_HEIGHT)}
            }

# Base colors
RED    =   const(0x07E0)
GREEN  =   const(0x001f)
BLUE   =   const(0xf800)
CYAN   =   const(0x07ff)
YELLOW =   const(0xffe0)
WHITE  =   const(0xffff)
BLACK  =   const(0x0000)
GRAY   =   const(0xbdf7)

# A basic range of cold to heat colors
colors = ((1, 1, 1), (4, 4, 4), (21, 9, 5), (39, 15, 6), (57, 21, 7), (75, 26, 9),
          (92, 32, 10), (110, 38, 11), (128, 43, 12), (146, 49, 14), (163, 55, 15),
          (181, 60, 16), (199, 66, 18), (217, 72, 19),(217, 78, 28), (199, 85, 44),
          (181, 92, 60), (163, 99, 76), (146, 106, 92), (128, 113, 108), (110, 120, 124),
          (92, 127, 140), (75, 134, 156), (57, 141, 172), (39, 148, 188), (21, 155, 204), (4, 162, 221))  #26 values

COLORS_RANGE = const(26)

# Globals
running = True                        # !!!!  definir melhor esta flag global: fica só no payload?
data_bus = Payload()

# classes
class Lock:
    def __init__(self):
        self._locked = lock

    def acquire(self, timeout=0):
        """
            Tries to acquire the lock in the specified time.

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

# --Bar----------------------------------------------------------------------------------------->

class BarWindow():
    """ Class that builds and runs a bar window """
    
    # core methods       
    def __init__(self, display, data):
        self.type = 'bar'
        self.on = True
        self.current = False
        self.background_color = WHITE
        self.foreground_color = BLACK
        self.highlight_color = BLUE        
        self.highlighted = False   
        self.data = data
        self.pages = data.pages
        self.frame = data.frame
        self.display = display
        self.configs = data.configs
        (self.column, self.line) = Window_shapes[self.type]['place']
        (self.width, self.height) = Window_shapes[self.type]['size']
        self.x_offset, self.y_offset = self.configs.bar_x_offset, self.configs.bar_y_offset
        self._frame_lock = Lock()
        self.timeout = 1
        self.touch = None
        self.current_page = 0
        self.current_field = 0
        self.current_zone = 0
        self.columns = COLUMNS
        
    def show(self, setting=True):
        self.on = setting
        
    def set(self, x_offset, y_offset):
        self.configs.bar_x_offset, self.configs.bar_y_offset = x_offset, y_offset

    def get(self, touch_coordinates):
        self.touch = self.get_bar_touch(touch_coordinates)
        return self.touch

    def clear(self):
        self.clear_bar()
        
    def render(self):
        if self.on:
            self.render_bar(self.pages, self.x_offset, self.y_offset)
 
    # helper methods        
    def get_bar_touch(self, touch_coordinates):   # used to pick and adjust field values and icons
        
        # offset coordinates
        (x, y) = touch_coordinates
        x -= self.x_offset
        y -= self.y_offset
        
        # check if touch area is acceptable 
        if x > self.column:
            self.current_field = max(0, min(y // FIELD_STEP, 7))
            self.current_zone = max(0, min((x - self.column) // ZONE_STEP, 2))
            return (self.current_field, self.current_zone)    # field from 0 to 7 and zone (in each field) from 0 to 2               
    
    def check_touch(self, page):
        """ Executes actions based on page type and touched area"""
            
        # if page is a menu or radiobutton, get choice
        if page['type'] in ['menu','input']:
            if self.current_field is not None:
                if self.current_field > 0 and self.current_field < 6:
                    page['fields'][page['value']-1]['value'] = False
                    page['fields'][self.current_field-1]['value'] = True
                    page['value'] = self.current_field
                    
#        elif ... for all other cases...
            
    def clear_bar(self, x_offset=0, y_offset=0, color=WHITE):
        """ clear all pages """

        self.display.set_buffer('bar')
        for column in range(5-self.columns,5):             ##  TEM de ser controlado: nr_of_columns é const
            self.clear_column(column, x_offset, y_offset, color)
            
    def clear_column(self, column, x_offset, y_offset, color=WHITE):
        """ clear all fields of a page """

        for line in range (8):
            self.display.set_block(x_offset + self.column + column * FIELD_BLOCK_WIDTH,
                                   y_offset+ self.line + line * FIELD_BLOCK_HEIGHT,
                                   FIELD_BLOCK_WIDTH,
                                   FIELD_BLOCK_HEIGHT)
            self.display.fill(color)
            self.display.show_block()

    def set_highlight(self, highlighted=True, color=RED):
        self.highlighted = highlighted
        self.highlight_color = color
            
    # renderers
    def render_bar(self, pages=None, x_offset=0, y_offset=1):
        """Renders bar window text and graphic blocks to LCD.

        TO DO LIST:
            -        
        ERRORS:
            - 
        """

        self.display.set_buffer('bar')
        self.current_page = 4                                   ## current_page terá de ser atualizada...
        
        if pages:
            
            # for all blocks
            for column in range(self.columns):             ##  self.columns te de ser atualizada de acordo com cada page
            # bar may have 1 to n columns (pages), from right to left:
                if pages[self.current_page]:  
                    self.check_touch(pages[self.current_page])                    
                    self.render_page(pages[self.current_page], column, x_offset, y_offset)
                else:
                    self.clear_column(column, x_offset, y_offset)
        else:
            self.clear_bar(x_offset, y_offset)

    def render_page(self, page, column, x_offset, y_offset):
        # column index (0-n) is from right to left

        if page:
            # render header
            self.render_header(page, column, x_offset, y_offset)

            # render fields
            self.render_fields(page, column, x_offset, y_offset)
        
    
    def render_header(self, page, column, x_offset, y_offset):
        
        self.display.set_block(x_offset + self.column + column * FIELD_BLOCK_WIDTH,
                               y_offset + self.line,
                               FIELD_BLOCK_WIDTH,
                               FIELD_BLOCK_HEIGHT)

        if page['subtitle'] in ['Message', 'Warning', 'Spot']:
            background = BLUE
        else:
            background = RED

        # highlight, eventually
        if self.highlighted:
            color_1 = background
            color_2 = GRAY
        else:
            color_1 = WHITE
            color_2 = background
            
        self.render_field(color_1, f"{page['title']:^12}", 0, color_2, f"{page['subtitle']:^12}", 0)
        self.display.show_block()
                        
                     
    def render_fields(self, page, column, x_offset, y_offset):

########  Completar
# 
# text input/output fields
# icon fields

        line = 1
        for field in page['fields']:
            
            self.display.set_block(x_offset + self.column + column * FIELD_BLOCK_WIDTH,
                                   y_offset + self.line + line * FIELD_BLOCK_HEIGHT,
                                   FIELD_BLOCK_WIDTH,
                                   FIELD_BLOCK_HEIGHT)
            
            if field:
                if field['active']:
                    
                    # menu field
                    if field['type'] == 'menu':
                        if field['value']:                        
                            text_color = WHITE
                            background_color = BLUE
                        else:
                            text_color = BLUE
                            background_color = WHITE
                            
                        self.render_field(text_color, field['name'], 4, background_color)

                    # temperatures output field
                    elif field['type'] == 'temperature':
                        if field['value'] in ['center', 'average', 'max', 'min', 'spot']:
                            self.render_field(RED, field['name'], 10, WHITE, f"{self.data.temperatures[field['value']]:.2f}" + " C", 15)
                        
                    # radio button fields
                    elif field['type'] == 'radio':
                        if field['value']:
                            text_color = WHITE
                            background_color = BLUE
                        else:
                            text_color = BLACK
                            background_color = GRAY
                            
                        self.render_field(text_color, field['name'], 10, background_color)

                    # message fields
                    elif field['type'] == 'message':
                        self.render_field(BLUE, field['name'], 10, WHITE, field['value'], 10)          

                    # dropdown menu fields
                    elif field['type'] == 'dropdown':
                        ####   Necessita de fazer o rendering em modo de edição (+/-/Enter)
                        self.render_field(BLACK, field['name'], 10, GRAY, field['list'][field['value']], 10)

                    # knobfields
                    elif field['type'] == 'knob':
                        ####   Necessita de fazer o rendering em modo de edição (+/-/Enter)
                        self.render_field(BLACK, field['name'], 10, GRAY, f"{field['value']:.2f}", 10)
                
                else:
                    self.display.fill(WHITE)
            else:
                self.display.fill(WHITE)
            
            line += 1            
            self.display.show_block()

                    
    def render_field(self, f_color, text_1, tab_1, b_color=0, text_2="", tab_2=0):
            
        if b_color != 0:            
            self.display.fill(b_color)
        
        self.display.text(text_1, tab_1, 10, f_color)
        if text_2!="":
            self.display.text(text_2, tab_2, 25, f_color)
                        
# --Strip----------------------------------------------------------------------------------------->>

class StripWindow():
    """ Class that builds and runs a strip window"""
    
    # core methods   
    def __init__(self, display, data):
        self.type = 'strip'
        self.on = True
        self.current = False
        self.background_color = WHITE
        self.foreground_color = BLACK
        self.highlight_color = BLUE        
        self.highlighted = False        
        self.data = data
        self.pages = data.pages
        self.display = display
        self.configs = data.configs
        (self.column, self.line) = Window_shapes[self.type]['place']
        (self.width, self.height) = Window_shapes[self.type]['size']
        self.x_offset, self.y_offset = self.configs.strip_x_offset, self.configs.strip_y_offset
        self.minimum = self.configs.minimum_temperature
        self.maximum = self.configs.maximum_temperature
        self.calculate_colors = self.configs.calculate_colors
        self.current_field = 0
        self.current_zone = 0
        self.touch = (0, 0)

    def show(self, setting=True):
        self.on = setting
    
    def set(self, x_offset=0, y_offset=0, levels=0, mode=0):
        self.configs.strip_x_offset,
        self.configs.strip_y_offset,
        self.configs.levels,
        self.configs.mode = x_offset, y_offset, levels, mode
    
    def get(self, touch_coordinates):
        self.touch = self.get_strip_touch(touch_coordinates)
        return self.touch
    
    def clear(self):
        self.clear_strip()
    
    def render(self):
        if self.on:
            self.render_strip(self.configs, self.x_offset, self.y_offset)

    # helper methods                    
    def get_strip_touch(self, touch_coordinates):  # used to adjust the max and min strip values
        """ Gets the (field, zone) of the touched strip fields
            - a field is a window area (a rectangle with 3 zones: left, middle, right)
            - a touched object is referenced by:  (field_ID,zone_ID), eg. (3,0)
        """   

        # offset coordinates
        (x, y) = touch_coordinates
        x -= self.x_offset
        y -= self.y_offset

        # check if touch area is acceptable
        if y > self.line:                      # y_point
            self.current_field = max(0, min(x // BLOCK_STEP, 5))
            self.current_zone = max(0, min((x % BLOCK_STEP) // ZONE_STEP, 2))
            return (self.current_field,self.current_zone)    # field from 0 to 3 and zone (in each field) from 0 to 2               

    def check_touch(self):
        """ Executes actions based on page type and touched area

            DO IT!!!
            
        """
        pass            


    def clear_strip(self, x_offset=0, y_offset=0, color=WHITE):

        self.display.set_buffer('bar')
        
        for column in range(4):             ##  TEM de ser controlado: nr_of_columns é const
            self.display.set_block(x_offset + self.column + column * FIELD_BLOCK_WIDTH,
                                   y_offset + self.line ,
                                   FIELD_BLOCK_WIDTH,
                                   FIELD_BLOCK_HEIGHT)
            self.display.fill(color)
            self.display.show_block()
            
            
    def set_highlight(self, highlighted=True, color=BLUE):
        self.highlighted = highlighted
        self.highlight_color = color

    # renderers
    def render_strip(self, configs=None, x_offset=0, y_offset=0):
        """Renders color temperature scale (heat palette)"""

        # highlight, eventually
        if self.highlighted:
            color = self.highlight_color
        else:
            color = WHITE
        
        
        # Palette Modes (False= min/max input, True=min/max from frame)
        if self.data.configs.max_min_set:
            self.maximum, self.minimum = self.data.temperatures['max'], self.data.temperatures['min']
        
        self.display.set_buffer('strip')
        self.check_touch()

        for block in range(4):

            self.display.set_block(x_offset + block * FIELD_BLOCK_WIDTH, y_offset + self.line, FIELD_BLOCK_WIDTH-1, FIELD_BLOCK_HEIGHT)
            self.display.fill(color)
            if configs:
                self.render_strip_block(configs, block) 
            self.display.show_block()
  
    def render_strip_block(self, configs, block):
        """Renders strip block (temperature color scale) to LCD"""
     ######
        #####  Melhorar
        #####
        
        block_color_range = configs.color_range // 6 if block == 0 or block == 3 else configs.color_range // 3 
        offset_x = BLOCK_STEP // 2 + 12 if block == 0 else 0
        offset_y = 6
        
        strip_pixel_x = (BLOCK_STEP * 3) // configs.color_range - 2
        strip_pixel_y = STRIP_WINDOW_HEIGHT - 20
        
        # Draw pixels
        for i in range(block_color_range):
            color = FrameWindow.get_color(self, i + block * (configs.color_range // 3 - 1), type=1)
            self.display.fill_rect(offset_x + i*strip_pixel_x, offset_y, strip_pixel_x, strip_pixel_y, color)
        
        # highlight, eventually
        if self.highlighted:
            max_color = WHITE
            min_color = BLACK
        else:
            max_color = RED
            min_color = BLUE
        
        # Print max/min temps
        if block == 3:
            self.display.text(f"{self.maximum:.1f}", BLOCK_STEP // 2 , 12, max_color)
        elif block == 0:
            self.display.text(f"{self.minimum:.1f}", 15, 12, min_color)

# --Frame----------------------------------------------------------------------------------------->>>
       
class FrameWindow():
    """ Class that builds a frame window"""
    
    # core methods
    def __init__(self, display, data):
        self.type = 'frame'
        self.on = True
        self.current = False
        self.background_color = BLACK
        self.foreground_color = WHITE
        self.highlight_color = RED
        self.highlighted = False
        self.data = data
        self.frame = data.frame
        self.pages = data.pages
        self.display = display
        self.configs = data.configs
        (self.column, self. line) = Window_shapes[self.type]['place']
        (self.width, self.height) = Window_shapes[self.type]['size']
        self.x_offset, self.y_offset = self.configs.frame_x_offset, self.configs.frame_y_offset
        self.maximum = self.configs.maximum_temperature
        self.minimum = self.configs.minimum_temperature
        self.delta = self.maximum - self.minimum
        self.calculate_colors = self.configs.calculate_colors
        self.interpolate_pixels =  self.configs.interpolate_pixels
        self._frame_lock = Lock()
        self.timeout = 1
        self.current_x_pixel, self.current_y_pixel = 16, 12
        self.touch = (0, 0)
        self.pixel_size = FRAME_STEP // 16 if self.interpolate_pixels else FRAME_STEP // 8
        self.x_pixels =  63  if self.interpolate_pixels else 31
        self.y_pixels =  47  if self.interpolate_pixels else 23
        self.pixels = 16 if self.interpolate_pixels else 8
        self.spot_color = WHITE

        
    def show(self, setting=True):
        self.on = setting    
    
    def set(self, x_offset=0, y_offset=0, interpolate=False, calculate=False):
        self.configs.frame_x_offset, self.configs.frame_y_offset, self.configs.interpolate_pixels, self.configs.calculate_colors = self.x_offset, self.y_offset, self.interpolate_pixels, self.calculate_colors = x_offset, y_offset, interpolate, calculate_colors
    
    def get(self, touch_coordinates):
        self.touch = self.get_frame_touch(touch_coordinates)
        return self.touch
    
    def clear(self):
        self.clear_frame()
    
    def render(self):
        if self.on:
            self.render_frame(self.frame, self.x_offset, self.y_offset, self.interpolate_pixels)

    # helper methods
    
    def get_temperatures(self,frame, index=SOURCE_SIZE):
        """ gets a list of temperatures (center, average, max, min, spot)"""
        if self._frame_lock.acquire(self.timeout):
            try:
                # center temperature
                self.data.temperatures['center'] = (frame[383]+frame[384])/2     
                # average temperature
                self.data.temperatures['average'] = sum(frame) / SOURCE_SIZE
                # maximum temperature
                self.data.temperatures['max'] = max(frame)
                # minimum temperature
                self.data.temperatures['min'] = min(frame)     
                # temperature at position
                if index >=0 and index < SOURCE_SIZE:
                    self.data.temperatures['spot'] = frame[index]
                else:
                    self.data.temperatures['spot'] = frame[self.current_x_pixel + 32 * (23-self.current_y_pixel)]
            finally:
                self._frame_lock.release()
        else:
            raise Exception("Buffer in use by other process.")
        
    def get_temperature(self, index, frame, interpolate=False):
        """Get temperature for pixel referenced by index:
            if not interpolate: get temperature from frame[index]
            if interpolate: get temperature from Gaussian interpolation method that doubles frame in each dimension
        """
        
        if not interpolate:
            # use pixels from frame
            if self._frame_lock.acquire(self.timeout):
                try:
                    return frame[index]
                finally:
                    self._frame_lock.release()
            else:
                raise Exception("Buffer in use by other process.")
                return 
        
        # interpolate new pixels
        pix = 0.0            
        sourceAddress = ((index >> 1) & 0x1f) + ((index & 0xffffff80) >> 2)            
        q = (index & 0x00000001) + ((index & 0x00000040) >> 5);   
        
        # apply all 4 operations of the kernel
        if self._frame_lock.acquire(self.timeout):
            try:
                for z in range(4):                
                    
                    # get and clamp the source adress
                    sa = (sourceAddress + Interpolation_offsets[q][z]) % SOURCE_SIZE
                    pix += Kernel[q][z] * frame[sa]
            finally:
                self._frame_lock.release()
        else:
            raise Exception("Buffer in use by other process.")
        return pix                   

    def get_color(self, value, type=0):
        """ Heatmap: returns an RGB565 color representing value"""
        
        if type == 0:
            # clip value
            value = max(self.minimum, min(value, self.maximum))

            # Normalize value to a 0-1 range
            ratio = (value - self.minimum) / self.delta
        else:
            ratio = value / self.configs.color_range
                       
        # get RGB
        if self.calculate_colors:
            b = max(0, int(255*(1 - ratio)))
            r = max(0, int(255*(ratio - 1)))
            g = 255 - b - r
        else:
            ratio = int(ratio * self.configs.color_range)
            (r,g,b) = colors[ratio]
        return (r & 0xf8) << 8 | (g & 0xfc) << 3 | b >> 3
    
    def get_frame_touch(self, touch_coordinates):  # used to spot a pixel on frame
        """ Gets the (col, lin) of the touched pixel """
        
        # offset coordinates
        (x, y) = touch_coordinates
        x -= self.x_offset
        y -= self.y_offset
        
        # check if touch area is aceptable
        if (x < self.width and y < self.height):
            self.current_x_pixel =  max(0, min(x // self.pixel_size, self.x_pixels))
            self.current_y_pixel = max(0, min(y // self.pixel_size, self.y_pixels))
            return (self.current_x_pixel, self.current_y_pixel)

    def check_touch(self):
        """ Executes actions based on page type and touched area """
        
        if self.current:
            self.display.draw_pixel(self.x_offset + self.current_x_pixel * self.pixel_size,
                                    self.y_offset + self.current_y_pixel * self.pixel_size,
                                    self.pixel_size,
                                    self.pixel_size,
                                    self.spot_color)
            
    def clear_frame(self, x_offset=0, y_offset=0, color=BLACK):        
        self.display.set_buffer('frame')        
        for line in range(3):
            for column in range(4):
                self.clear_block(column, line, x_offset, y_offset, color)
            
    def clear_block(self, column, line, x_offset, y_offset, color):
        """ clear all frame blocks """
        self.display.set_block(x_offset + column * BLOCK_STEP, y_offset + line * BLOCK_STEP, BLOCK_STEP-1, BLOCK_STEP-1)
        self.display.fill(color)
        self.display.show_block()

    def set_highlight(self, highlighted=True, color=RED):
        self.highlighted = highlighted
        self.highlight_color = color

    # renderers
    def render_frame(self, frame=None, x_offset=0, y_offset=0, interpolate=False):
        """Renders all frame window blocks (temperature plot from sensor) to LCD"""
        
        # highlight, eventually
        if self.highlighted:
            background_color = self.highlight_color
        else:
            background_color = BLACK
        
        self.display.set_buffer('frame')
        if frame:
            self.get_temperatures(frame)

            # for all blocks
            for block_j in range(3):
                block_y = block_j * FRAME_STEP + y_offset
                for block_i in range(4):                
                    block_x = block_i * FRAME_STEP + x_offset
                    self.display.set_block(block_x, block_y, BLOCK_STEP-1, BLOCK_STEP-1)
                    self.render_frame_block(frame, block_i, block_j, interpolate)
                    self.display.show_block()
            self.check_touch()

        else:
            self.clear_frame(x_offset, y_offset, background_color)

    def render_frame_block(self, frame, block_i, block_j, interpolate=False):
        """ Renders an individual block of a frame """

        j_step = 64 if interpolate else 32
        j_max =  47 if interpolate else 23
        j_offset = self.pixels * block_j
        i_offset = self.pixels * block_i
        
        # for all pixels
        for pixel_j in range(self.pixels):
            pixel_y = pixel_j * self.pixel_size
            j = j_max - j_offset - pixel_j
            for pixel_i in range(self.pixels):
                pixel_x = pixel_i * self.pixel_size
                i = i_offset + pixel_i
                index = i + j * j_step
                color = self.get_color(self.get_temperature(index, frame, interpolate))
                self.display.fill_rect(pixel_x, pixel_y, self.pixel_size,self.pixel_size, color)

# --Manager----------------------------------------------------------------------------------------->>>>

class WindowManager:
    """ Window Management"""
    
    def __init__(self, display, data):
        self.display = display
        self.data = data
        self.windows = []
        self.current_window = None

    def add_window(self, window):
        self.windows.append(window)
        
    def get_windows(self):
        return self.windows
        
    def delete_window(self, window):
        result = 0
        try:
            self.windows.remove(window)
        except ValueError as e:
            print(f"Error: {e}")
            result = -1
        return result
        
    def set_current_window(self, window):
        if self.current_window is not None:
            self.current_window.current = False
        self.current_window = window
        self.current_window.current = True
#        self.render_window(window)

    def render(self):
        for window in self.windows:
            window.render()
        
    def render_window(self, window):
        window.render()
        
    def create_windows(self, windows):
        # Create and register windows in WindowsManager
        
        for Win in windows:
            Window = Win(self.display, self.data)
            self.add_window(Window)
#            Window.clear()

# --Input----------------------------------------------------------------------------------------->>>>>

# Input handling (button or touch)
class InputHandler:
    """ Input and decision making """
    
    def __init__(self, window_manager):
        self.window_manager = window_manager
        # Set up input (buttons or touch)

    def check_input(self):
        # Implement input logic to get user input and switch windows

# Uncomment bellow to use interrupts:       
#        self.window_manager.display.get_touch()
        
        # get the touched display coordinates and act upon them
        touch_coordinates = self.window_manager.display.touch_coordinates           
        if self.window_manager.display.touch_active and touch_coordinates is not None:
            
            touched_window = self.get_touched_window(touch_coordinates)
            
            print(touch_coordinates, touched_window)
            
            if self.window_manager.current_window is None:
                self.window_manager.set_current_window(self.get_window(touched_window))
            else:
                if touched_window != self.window_manager.current_window.type:
                    # change focus (new window)
                    
                    self.window_manager.current_window.set_highlight(False)                    
                    self.window_manager.set_current_window(self.get_window(touched_window))
                    self.window_manager.current_window.set_highlight(True)

                    # ...
                            
            # check which field was touched
            touched_field = self.window_manager.current_window.get(touch_coordinates)
            if touched_field is not None:
                
                # show here the focus field!!! highlight field
                
                print(touched_field)
            
                # do something with the touched field/pixel or leave it to render functions in windows??? 
            
            self.window_manager.display.touch_active = False
            self.window_manager.display.touch_coordinates = None
    
    def get_window(self, window):
        """ Gets the window object of from a window label"""
        for _win in self.window_manager.windows:
            if _win.type == window:
                return _win
        return None
    
    def get_touched_window(self, touch_coordinates):  # used to identify which window was touched
        """ Gets the label of a touched window """
        (x, y) = touch_coordinates
        # check touch area            
        if x < FRAME_WINDOW_WIDTH:
            if y < FRAME_WINDOW_HEIGHT:
                return 'frame'
            else:
                return  'strip'
        return 'bar'

# --Screen----------------------------------------------------------------------------------------->>>>>>
# The full thing: A Thermal Camera!

class Screen():
    """ Thermal Camera class"""

    win = [FrameWindow, BarWindow, StripWindow]     # Window objects to be instanced (shown)

    def __init__(self):
        
        global data_bus
        
        self.data = data_bus
        self.display = Display()
        self.windows_manager = WindowManager(self.display, data_bus)
        self.windows_manager.create_windows(self.win)                
        self.windows_manager.set_current_window(self.windows_manager.get_windows()[0])       # initial focus window
        self.windows_manager.current_window.clear()
        self.input_handler = InputHandler(self.windows_manager)

    def loop(self, running=True):
        # Main loop
        
        while running:
#            stamp = time.ticks_ms()
            
            self.input_handler.check_input()
            gc.collect()
            self.windows_manager.render()
            gc.collect()


            # An alternative with input handling per window render...
            
#             for window in self.windows_manager.windows:
#                  self.input_handler.check_input()
#                  gc.collect()
#                  self.windows_manager.render_window(window)
#                  gc.collect()
                        
#            time.sleep(0.5)

#            print("Gets one screen rendered in %0.4f ms" % (time.ticks_diff(time.ticks_ms(), stamp)))        
#            print("Screen: Used RAM:", gc.mem_alloc(), "Remaining RAM:", gc.mem_free())
            

if __name__=='__main__':
    
    # setup context
    minimum_temperature = 0.0
    maximum_temperature = 100.0
    temperatures = {'center': 23.0,
                             'average': 24.1,
                             'max': 26.2,
                             'min': 23.1,
                             'spot': 24.0}

    # create a dummy frame
    frame = [0] * 768
    for j in range(0,24):
        for i in range(0,32):
            frame[i+32*j]= i*j/6

    # stuff data_bus
    data_bus = Payload()
    data_bus.frame = frame
    data_bus.configs.minimum_temperature = minimum_temperature
    data_bus.configs.maximum_temperature = maximum_temperature
#     data_bus.configs.frame_x_offset = 20
#     data_bus.configs.frame_y_offset = 20
    
    # launch windows
    camera = Screen()
    camera.loop()
