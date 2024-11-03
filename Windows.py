"""
 Graphic User Interface for Thermal Cam based on
 Raspberry pi Pico, MLX90640 IR sensor, ILI9488/XPT2046 Touch LCD 
================================================================================


* Author(s): Paulo Teixeira


Implementation Notes
--------------------

**Software and Dependencies:**


Windows is a simple GUI class that creates, organizes and renders windows for the MLX90640 Thermal Camera.
Windows depends on Display and is structured around:
    
    - Block: a display area that can be used in mosaics to form windows. Blocks need buffers
        
    - Window: a group of blocks that shows content and read user input (touched objects in screen)
    
    - Screen: a group of Windows:       
        - Frame window: 4 x 3 frame blocks at the left side of the screen (block buffer - show pixels and text)
        - Bar window: 1-5 x 5 bar blocks at the right side of the screen (bar buffer - show pictures (Icons) and text)
        - Strip Window: 2 strip_block at bottom side of the screen  (strip buffer - show pixels and text)
        
        - Frame and Bar may overlap , needing to implement a focus mechanism
        
        - blocks used in frame window use frame_buffer and show text and pixels
        - blocks used in bar window use bar_buffer and show text and icons
        - blocks used in strip window use strip_buffer and show pixels and text
          
        - Screen is managed by WindowsManager
        - User input is managed by InputHandler
TODOS:
    - Remake Bar renderer!
    - Complete Strip with modes, auto min/max and temperature labels
    - Complete Frame with cursor and temperature labels
    - Make InputHandler logic (status, content page navigation, user inputs, actions)
    - Touch get functions need change

ERRORS:

"""
    
from Display import Display
from Sensor import lock, running
import time
import gc
from Context import content, CONTENT_PAGES


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
DISPLAY_WIDTH = const(480)
DISPLAY_HEIGHT = const(320)

BLOCK_STEP = const(96)
STRIP_STEP = const(32)
TEXT_STEP = const(24)
FIELD_STEP = const(2*TEXT_STEP)

FRAME_BLOCK_WIDTH = const(BLOCK_STEP)
FRAME_BLOCK_HEIGHT = const(BLOCK_STEP)
BAR_BLOCK_WIDTH = const(BLOCK_STEP)
BAR_BLOCK_HEIGHT = const(FIELD_STEP)
STRIP_BLOCK_WIDTH = const(2 * BLOCK_STEP)
STRIP_BLOCK_HEIGHT = const(STRIP_STEP)

FRAME_WINDOW_WIDTH = const(4 * FRAME_BLOCK_WIDTH)
FRAME_WINDOW_HEIGHT = const(3 * FRAME_BLOCK_HEIGHT)
BAR_WINDOW_WIDTH = const(5 * BAR_BLOCK_WIDTH)
BAR_WINDOW_HEIGHT = const(4 * BAR_BLOCK_HEIGHT)
STRIP_WINDOW_WIDTH = const(2 * STRIP_BLOCK_WIDTH)
STRIP_WINDOW_HEIGHT = const(STRIP_BLOCK_HEIGHT)

SOURCE_SIZE = const(768)

Window_shapes = {
            'Frame':
                {'size': (FRAME_WINDOW_WIDTH, FRAME_WINDOW_HEIGHT),
                 'place':(0, 0)},
            'Bar':
                {'size': (BAR_WINDOW_WIDTH, BAR_WINDOW_HEIGHT),
                 'place':(FRAME_WINDOW_WIDTH, 0)},
            'Strip':
                {'size': (STRIP_WINDOW_WIDTH, STRIP_WINDOW_HEIGHT),
                 'place':(0, FRAME_WINDOW_HEIGHT)}
            }


# Base colors
RED    =   const(0x07E0)
GREEN  =   const(0x001f)
BLUE   =   const(0xf800)
CYAN   =   const(0x07ff)
YELLOW =   const(0xffe0)
WHITE  =   const(0xffff)
BLACK  =   const(0x0000)
GRAY   =   const(0xd69a)

# A basic range of cold to heat colors
colors = ((1, 1, 1), (4, 4, 4), (21, 9, 5), (39, 15, 6), (57, 21, 7), (75, 26, 9),
          (92, 32, 10), (110, 38, 11), (128, 43, 12), (146, 49, 14), (163, 55, 15),
          (181, 60, 16), (199, 66, 18), (217, 72, 19),(217, 78, 28), (199, 85, 44),
          (181, 92, 60), (163, 99, 76), (146, 106, 92), (128, 113, 108), (110, 120, 124),
          (92, 127, 140), (75, 134, 156), (57, 141, 172), (39, 148, 188), (21, 155, 204), (4, 162, 221))  #26 values

COLORS_RANGE = const(26)

# Global Flags
lock = False
running = True

# classes

class Lock:
    def __init__(self):
        self._locked = lock

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
            # Pequena pausa para evitar uso excessivo da CPU
            time.sleep(0.01)  # 10 ms

    def release(self):
        """
        Liberate lock.
        """
        self._locked = False
        
        
class Payload():
    # Global Camera data registers
    """
        frame:
            - 32 x 48 temperature (float) from sensor
            
        content:
            - array of Pages:
                 - dictionary of Fields
                    - Name
                    - Value (Text, Icon)
                     other to implement
                        - Type (Text, Icon)
                        - Touch (No, Left/Middle/Right)
                        - Position on field (I, J)
        temperatures:
            - list of temperatures (Average, Center, Min, Max, Spot)
        configs:
            - object with camera's configs
    """
    frame = []
    content = []
    temperatures = [0.0,0.0,0.0,0.0,0.0]
    configs = None
            
class Configs():
    # Global Camera Configurations
    
    # Mode
    interpolate_pixels = False
    calculate_colors = False
    
    # Position
    frame_x_offset = 0
    frame_y_offset = 0
    bar_x_offset = 0
    bar_y_offset = 0
    strip_x_offset = 0
    strip_y_offset = 0
    
    # Palette
    minimum_temperature = 0.0
    maximum_temperature = 100.0
    temperature_delta = 100.0
    max_min_set = False               #if True then get min/max from frame
    color_range = COLORS_RANGE
    
    def store(self):
        # serialize config data and store in sd card
        pass
    
    def set_palette(self, maximum=0.0, minimum=100.0, calculate=True):
        """Sets the temperatures for color palette"""
        self.minimum_temperature = maximum
        self.maximum_temperature = minimum
        self.temperature_delta = maximum - minimum
        self.calculate_colors = calculate

# --Bar-----------------------------------------------------------------------------------------> 
class BarWindow():
    def __init__(self, display, payload):
        self.type = 'Bar'
        self.payload = payload
        self.content = payload.content
        self.frame = payload.frame
        self.temperatures = payload.temperatures
        self.display = display
        self.configs = payload.configs
        (self.column, self. line) = Window_shapes[self.type]['place']
        (self.width, self.height) = Window_shapes[self.type]['size']
        self._frame_lock = Lock()
        self.timeout = 1

    def set(self, x_offset, y_offset):
        self.configs.bar_x_offset, self.configs.bar_y_offset = x_offset, y_offset
    
    def get(self):
        touch = self.get_bar_touch()
        if touch != None:
            (self.touched_field, self.touched_zone) = touch
        return touch

    def clear(self):
        self.render_bar()
        
    def render(self):
        self.render_bar(self.content, self.configs.bar_x_offset, self.configs.bar_y_offset)
 
    # helper methods
    def get_temperatures(self,framebuf, index=SOURCE_SIZE):
        """ gets a list of temperatures (center, average, max, min, index)"""
        if self._frame_lock.acquire(self.timeout):
            try:
                # center temperature
                self.temperatures[0] = (framebuf[383]+framebuf[384]+framebuf[351]+framebuf[352]+framebuf[415]+framebuf[416])/6     
                # average temperature
                self.temperatures[1] = sum(framebuf) / SOURCE_SIZE
                # maximum temperature
                self.temperatures[2] = max(framebuf)
                # minimum temperature
                self.temperatures[3] = min(framebuf)     
                # temperature at position
                if index >=0 and index < SOURCE_SIZE:
                    self.temperatures[4] = framebuf[index]
                else:
                    self.temperatures[4] = 0.0
            finally:
                self._frame_lock.release()
        else:
            raise Exception("Buffer in use by other process.")
                        

    def get_bar_touch(self):   # used to pick and adjust field values and icons
        ZONE_SIZE = BLOCK_STEP/3
        (touched_field, touched_zone) = (0,0)
        touch_point = self.display.get_touch()
        if touch_point != None:
            [X_Point,Y_Point] = touch_point
            
            # check if touch area is acceptable
            if X_Point > FRAME_WINDOW_WIDTH:
                touched_field = Y_Point // FIELD_STEP                         # field from 0 to 6
                touched_zone = (X_Point - FRAME_WINDOW_WIDTH)// ZONE_SIZE     # zone (in each field) from 0 to 2
                return (touched_field, touched_zone)
        return None

    # renderers
    def render_bar(self, content=None, x_offset=0, y_offset=1):
        """Renders bar window text and graphic blocks to LCD."""
        
        self.get_temperatures(self.frame)

        #########  BAR may be n (0 to 4) columns, from right to left:
        #########  need anothe loop and content items must refer to a page

        self.display.set_buffer('bar')
        
        # for all blocks        
#        for i_block in range(CONTENT_PAGES):
        for i_block in range(4,CONTENT_PAGES):             ###########   TEM de ser controlado: nr_of_columns????
            for j_block in range(6):
                field = content[i_block][j_block]
                self.display.set_block(x_offset + i_block * BAR_BLOCK_WIDTH, y_offset + j_block * BAR_BLOCK_HEIGHT, BAR_BLOCK_WIDTH, BAR_BLOCK_HEIGHT)
                if field:
                    self.render_bar_block(field)
                else:
                    self.display.fill(WHITE)
                self.display.show_block()

    def render_field(self, field, f_color, key_1, tab_1, b_color=0, key_2="", tab_2=0):
        if b_color != 0:            
            self.display.fill(b_color)
        self.display.text(field[key_1], tab_1, 10, f_color)
        if key_2!="":
            self.display.text(field[key_2], tab_2, 25, f_color)
        
    def render_bar_block(self, field):
        #parses content (type: text, icon, read, values: x/y position) and prints to LCD

        if field:
            for key in field.keys():
                
                if key == 'Title':
                    self.render_field(field, WHITE, 'Title', 5, RED, 'Subtitle', 5)

                if key in ['Notice', 'Spot']:
                    self.render_field(field, WHITE, 'Title', 15, BLUE, 'Subtitle', 15)                   
                
                if key in ['Camera', 'Media', 'Mode', 'Setting']:
                    text_color = BLACK
                    background_color = WHITE
                    if field[key]:
                        background_color = GRAY
                        text_color = WHITE
                    
                    self.display.fill(background_color)
                    self.display.text(key, 15, 15, text_color)                       

                if key in ['Center', 'Average', 'Max', 'Min']:
                        self.render_field(field, BLACK, key, 15, WHITE)
                        self.display.text(field[key], 15, 25, RED)  
                        
                        
# ------------------------------------------------------------------------------------------->>

class StripWindow():
    def __init__(self, display, payload):
        self.type = 'Strip'
        self.payload = payload
#        self.content = payload.content
        self.display = display
        self.configs = payload.configs
        (self.column, self. line) = Window_shapes[self.type]['place']
        (self.width, self.height) = Window_shapes[self.type]['size']
        self.minimum = self.configs.minimum_temperature
        self.maximum = self.configs.maximum_temperature
        self.calculate_colors = self.configs.calculate_colors
        
    def set(self, x_offset, y_offset, levels, mode):
        self.configs.strip_x_offset,
        self.configs.strip_y_offset,
        self.configs.levels,
        self.configs.mode = x_offset, y_offset, levels, mode
    
    def get(self):
        touch = self.get_strip_touch()
        if touch != None:
            (self.touched_field, self.touched_zone) = touch
        return touch

    def clear(self):
        self.render_strip()
    
    def render(self):
        self.render_strip(self.configs, self.configs.strip_x_offset, self.configs.strip_y_offset)

    # helper methods                    
    def get_strip_touch(self):  # used to adjust the max and min strip values
        """ Gets the (field, zone) of the touched strip fields
            - a field is a window area (a rectangle with 3 zones: left, middle, right)
            - field_IDs are numbered from left to right (0 to 5)
            a touched object is referenced by:  (field_ID,zone), eg. (3,0)
        """
             
        ZONE_SIZE = BLOCK_STEP/3
        (touched_field, touched_zone) = (0,0)
        touch_point = self.display.get_touch()
        if touch_point != None:
            [X_Point,Y_Point] = touch_point
            
            # check if touch area is acceptable
            if Y_Point > FRAME_WINDOW_HEIGHT:
                touched_field = X_Point // FIELD_STEP                       # field from 0 to 4
                touched_zone = (X_Point % FIELD_STEP) // ZONE_SIZE            # zone (in each field) from 0 to 2
                return (touched_field, touched_zone)
        return None

    # renderers
    def render_strip(self, configs=None, x_offset=0, y_offset=0):
        """Renders color temperature scale (heat palette)"""
        
        # Palette Modes (False= min/max input, True=min/max from frame)
        if self.payload.configs.max_min_set:
            self.maximum, self.minimum = self.payload.temperatures[2], self.payload.temperatures[3]
        
        self.display.set_buffer('strip')
        
        for block in range(2):
            self.display.set_block(x_offset + block * STRIP_BLOCK_WIDTH, y_offset + FRAME_WINDOW_HEIGHT, STRIP_BLOCK_WIDTH-1, STRIP_BLOCK_HEIGHT)
            self.display.fill(WHITE)
            if configs:
                 self.render_strip_block(configs, block) 
            self.display.show_block()
  
    def render_strip_block(self, configs, block):
        """Renders strip block (temperature color scale) to LCD"""
        
        offset_x = const(BLOCK_STEP // 2 + 13)
        offset_y = const(4)
        
        strip_pixel_x = (STRIP_WINDOW_WIDTH - BLOCK_STEP - 20) // configs.color_range 
        strip_pixel_y = STRIP_WINDOW_HEIGHT - 8
        
        block_color_range = configs.color_range // 2
        # Draw pixels
        for i in range(0, block_color_range):
            
            color = FrameWindow.get_color(self,i + block * block_color_range, type=1)
            self.display.fill_rect(offset_x * (1-block)  + i*strip_pixel_x, offset_y, strip_pixel_x+1, strip_pixel_y, color)
        
        if block:
            self.display.text(f"{self.maximum:.1f}" + " C", STRIP_BLOCK_WIDTH - offset_x + 2, 12, RED)
        else:
            self.display.text(f"{self.minimum:.1f}" + " C", 5, 12, BLUE)

# ------------------------------------------------------------------------------------------->>>
       
class FrameWindow():
    def __init__(self, display, payload):
        self.type = 'Frame'
        self.frame = payload.frame
        self.content = payload.content
        self.display = display
        self.configs = payload.configs
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
        
    def set(self, x_offset, y_offset, interpolate, calculate):
        self.configs.frame_x_offset, self.configs.frame_y_offset, self.configs.interpolate_pixels, self.configs.calculate_colors = self.x_offset, self.y_offset, self.interpolate_pixels, self.calculate_colors = x_offset, y_offset, interpolate, calculate_colors
        
    def get(self):
        touch = self.get_frame_touch(self.configs.interpolate_pixels)
        if touch  != None:
            (self.x_pixel, self.y_pixel) = touch
        return touch
    
    def clear(self):
        self.render_frame()
    
    def render(self):
        self.render_frame(self.frame, self.x_offset, self.y_offset, self.interpolate_pixels)

    # helper methods                    
    def get_temperature(self, index, frame, interpolate=False):
        """Get temperature for pixel referenced by index:
            if not interpolate: temperature from frame[index]
            if interpolate: temperature from Gaussian interpolation method that doubles frame in each dimension
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
    
    def get_frame_touch(self, interpolate=False):  # used to spot a pixel on frame
        """ Gets the (col, lin) of the touched pixel """
        
        pixel_size = 6 if interpolate else 12
        
        touch_point = self.display.get_touch()
        if touch_point != None:
            [X_Point,Y_Point] = touch_point
            # check if touch area is aceptable
            if X_Point < FRAME_WINDOW_WIDTH and Y_Point < FRAME_WINDOW_HEIGHT:
                (i, j) = (X_Point // pixel_size, Y_Point // pixel_size)
                return (i, j)
        return None

    # renderers
    def render_frame(self, frame, x_offset=0, y_offset=0, interpolate=False):
        """Renders all blocks from frame window (temperature plot from sensor) to LCD"""
        
        # for all blocks
        self.display.set_buffer('frame')
        for block_j in range(3):
            block_y = block_j * BLOCK_STEP + y_offset
            for block_i in range(4):                
                block_x = block_i * BLOCK_STEP + x_offset
                self.display.set_block(block_x, block_y, BLOCK_STEP-1, BLOCK_STEP-1)
                if frame:
                    self.render_frame_block(frame, block_i, block_j, interpolate)
                else:
                    self.display.fill(BLACK)
                self.display.show_block()  

    def render_frame_block(self, frame, block_i, block_j, interpolate=False):
        """ Renders an individual block of a frame """
        
        pixels = 16 if interpolate else 8
        j_step = 64 if interpolate else 32
        j_max =  47 if interpolate else 23
        pixel_size = BLOCK_STEP // pixels
        j_offset = pixels * block_j
        i_offset = pixels * block_i
        
        # for all pixels
        for pixel_j in range(pixels):
            pixel_y = pixel_j * pixel_size
            j = j_max - j_offset - pixel_j
            for pixel_i in range(pixels):
                pixel_x = pixel_i * pixel_size
                i = i_offset + pixel_i
                index = i + j * j_step
                color = self.get_color(self.get_temperature(index, frame, interpolate))
                self.display.fill_rect(pixel_x, pixel_y, pixel_size,pixel_size, color)

# ------------------------------------------------------------------------------------------->>>>

class WindowManager:
    """ Window Management"""
    
    def __init__(self, display):
        self.display = display
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
        
    def set_window(self, window):
        self.current_window = window
        self.render_window(window)

    def render(self):
        for window in self.windows:
            window.render()
        
    def render_window(self, window):
        window.render()
        
# Input handling (button or touch)
class InputHandler:
    """ Input and decision making """
    
    def __init__(self, window_manager):
        self.window_manager = window_manager
        # Set up input (buttons or touch)

    def check_input(self):
        # Implement input logic to get user input and switch windows

        print(self.window_manager.current_window, self.window_manager.current_window.get())
#        self.window_manager.current_window.get()
        # ####  NEEDS NAVIGATION LOGIC !!!!
        # based on touched object:
        #  - define action
        #          change (up/down) / set (middle) field, 
        #          change (left/right) / set(middle) value,
        #          change (last/next) page,

# The full thing: A Thermal Camera!
class Screen():
    """ Thermal Camera class"""

    windows = [FrameWindow, BarWindow, StripWindow]     # Windows to be shown

    def __init__(self):
    
        self.display = Display()
        self.windows_manager = WindowManager(self.display)
        self.create_windows(self.windows)
        self.windows_manager.set_window(self.windows_manager.get_windows()[0])       # initial focus window
        self.input_handler = InputHandler(self.windows_manager)

    def loop(self, running=True):
        # Main loop
        
        while running:
#            stamp = time.ticks_ms()
            self.input_handler.check_input()
            self.windows_manager.render()
            gc.collect()
        #   time.sleep(0.1)
#            print("Gets one screen rendered in %0.4f ms" % (time.ticks_diff(time.ticks_ms(), stamp)))        
#            print("Screen: Used RAM:", gc.mem_alloc(), "Remaining RAM:", gc.mem_free())

    def create_windows(self, windows):
        # Create and register windows in WindowsManager
        
        for win in windows:
            self.windows_manager.add_window(win(self.display, Payload))

if __name__=='__main__':
    
    # setup context
    minimum_temperature = 0.0
    maximum_temperature = 100.0
    temperatures = [23.0,24.1,23.2,26.3,24.0]

    # create a dummy frame
    frame = [0] * 768
    for j in range(0,24):
        for i in range(0,32):
            frame[i+32*j]= i*j/6
    
    # stuff Payload
    Payload.frame = frame                    
    Payload.content = content
    Payload.configs = Configs()
    Payload.configs.minimum_temperature, Payload.configs.maximum_temperature = minimum_temperature, maximum_temperature
    
    # launch windows
    camera = Screen()
    camera.loop()
