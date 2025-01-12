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
        - Bar window: 1-5 x 5 field blocks at the right side of the screen (field and icon buffers - show pictures (Icons) and text)
        - Strip window: 1 x 4 field blocks at bottom side of the screen  (field and icon buffers - show pixels, icons, sprites and text)
        - Button window: 1 x 2 field blocks at right bottom side of the screen  (field and icon buffers - show icons, sprite and text)
        - Full: 4 x 4 frame blocks, fulfilling the whole dispplay (frame, field and icon buffers): takes full control 

    - Frame and Bar may overlap
      
    - Screen is managed by WindowsManager
    - User input is managed by InputHandler
    
TODOS:
    - States need to be better used!!!
    
    - Complete bar with modes, settings and card execution
    
    - Complete Strip with modes and min/max editing
    
    - Complete Frame with zoom, cursor and temperature labels
        - Frame Render
            - Improve performance
            - Print spot temperature in frame
    
ERRORS:

"""
from Display import Display
from Constants import *
import time
import gc


# Flags
DEBUG_STATES = False


# Classes

# tools
class Lock:
    # resource lock class
    
    def __init__(self, lock):
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

def debug_log(func):
    """
    Decorator to log debug messages if DEBUG_STATES is enabled.
    """
    def wrapper(self, window, *args, **kwargs):
        if DEBUG_STATES:
            action = func.__name__.replace("_", " ")
            action = action[0].upper() + action[1:].lower()
            print(f"{action} {window.type} in {self.__class__.__name__} state.")
        return func(self, window, *args, **kwargs)
    return wrapper

# states
class WindowState:
    """
        Window state class: Implements a state machine for all windows
        
    """
    
#    @debug_log
    def render(self, window, *args):
        # Add specific logic
        window.render_window(*args)
    
#    @debug_log        
    def touch(self, window, coordinates):
        # Add specific logic
        window.set_touch(coordinates)
    
#    @debug_log
    def clear(self, window):
        # Add specific logic
        window.clear_window()

#    @debug_log
    def touched(self, window):
        # Add specific logic
        window.check_touch()

class FocusedState(WindowState):
    
#    @debug_log
    def render(self, window, *args):
        # if full is the current window don't render other windows
        if window.type == 'full' or window.windows_manager.current_window.type != 'full':
            window.render_window(*args)
   
#    @debug_log
    def touched(self, window):
        if window.check_touch():
            # enter and exit full window
            if window.type == 'full':
                window.exit_full_state()
            elif window.type == 'bar':
                window.enter_full_state()


class IdleState(WindowState):
    
#    @debug_log
    def render(self, window, *args):
        # if current window is full dont render and only render frame when it is the current window
        if window.windows_manager.current_window:
            if window.type not in ['frame', 'full'] and window.windows_manager.current_window.type != 'full':
                window.render_window(*args)
    
#    @debug_log                
    def touched(self, window):
        window.check_touch()
        # if current window is full or button don't toggle between focused and idle states
        if window.type  not in ['button', 'full']:
            window.toggle_state()
        

class EditState(WindowState):
    pass

class HoldState(WindowState):
    pass


# Windows

class WindowBase:
    def __init__(self, windows_manager, type):
        self.windows_manager = windows_manager
        self.type = type
        self.state = IdleState()
        self.data = windows_manager.data
        self.frame = windows_manager.data.frame
        self.pages = windows_manager.data.pages
        self.display = windows_manager.display
        self.configs = windows_manager.data.configs
        (self.column, self.line) = Window_shapes[self.type]['place']
        (self.width, self.height) = Window_shapes[self.type]['size']
        self.background_color = self.data.colors.window_colors[self.type]['background']
        self.foreground_color = self.data.colors.window_colors[self.type]['foreground']
        self.header_color = self.data.colors.window_colors[self.type]['header']
        self.highlight_color = self.data.colors.window_colors[self.type]['highlight']
    
    def render(self):
        # Generic rendering logic
        pass
        
    def touch(self, touch_coordinates):
        # Captute touched field coordinates
        self.state.touch(self, touch_coordinates)
    
    def touched(self):
        # Generic touch processing logic
        self.state.touched(self)

    def clear(self):
        # Generic window clearing
        self.state.clear(self)

    def set_state(self, new_state: WindowState):
        # Set the window state
        self.state = new_state
    
    def toggle_state(self):
        # set this window as current and put it in FocusedState
            self.windows_manager.current_window.set_state(IdleState())
            self.windows_manager.set_current_window(self)
            self.set_state(FocusedState())
    
    def enter_full_state(self):
        # put Window in IdleState and set Full as current     
        self.set_state(IdleState())
        full_window = self.windows_manager.get_window(Window.FULL)     
        full_window.set_state(FocusedState())
        self.windows_manager.set_current_window(full_window)
            
    def exit_full_state(self):
        # put full window in IdleState and makes frame current and in FocusedState
        self.set_state(IdleState())
        frame_window = self.windows_manager.get_window(Window.FRAME)     
        frame_window.set_state(FocusedState())
        self.windows_manager.set_current_window(frame_window)
                    
    def clear_window(self):
        # Generic clearing logic
        pass

    def render_window(self):
        # Generic rendering logic
        pass

    def set_touch(self, coordinates):
        # Generic touch processing logic
        pass
    
    def check_touch(self):
        # Generic current window touch processing logic
        pass
    
    def check_button_touch(self, button_field, button_zone):
        # Generic button touch processing logic
        pass


class FullWindow(WindowBase):
    """ Class that builds and runs a general purpose full screen window"""
    
    # core methods   
    def __init__(self, windows_manager):
        self.type = 'full'
        super().__init__(windows_manager, self.type)
        
        self.current_x = None
        self.current_y = None
        self.x = None
        self.y = None
        self.content = {'idle': "ThermalCam", 'boot': "Welcome", 'calibrate': "Calibrate", 'shutdown': "Goodbye"}
        self.current_full_page = 'boot'
        self.changed = True
        self.calibration_level = self.data.configs.calibration_level
        
    # class interface
        
    def render(self):
        self.state.render(self, self.content)
        
    # helper methods
    
    def set_current_full_page(self, state):
        self.current_full_page = state
        self.changed = True
    
    def set_touch(self, touch_coordinates):
        """
            Sets the (x, y) coordinates of the touched display pixel 
        """   

        # plain display coordinates
        (self.x, self.y) = touch_coordinates
        
    def check_touch(self):
        """
            Executes actions based on touched area
        """
        
        # update current field/zone with lattest touch            
        self.current_x = self.x
        self.current_y = self.y
        self.x = None
        self.y = None
                
        if self.current_x is not None and self.current_y is not None:        
            
            # DO something here...    (change states, calibration points, etc and return True at the end...)
            
            if self.current_full_page != 'calibrate':
                self.windows_manager.get_window(Window.BUTTON).changed = True
                return True
            else:
                self.set_current_full_page('idle')
                return False
            
        return False
        
    def clear_window(self): 
        self.display.set_buffer('frame')
        self.display.fill(self.background_color)
        for line in range(FRAME_BLOCKS_HEIGHT+1):
            for column in range(FRAME_BLOCKS_WIDTH+1):
                self.display.set_block(column * BLOCK_STEP, line * BLOCK_STEP, BLOCK_STEP-1, BLOCK_STEP-1)
                self.display.show_block()            

            
    def set_highlight(self, color):
        self.highlight_color = color

    # renderers
    def render_window(self, content=None):
        """Renders full screen window"""
        
        def show_prompt(prompt=None):
            self.display.set_buffer('frame')
            self.display.fill(self.background_color)
            self.display.set_block(BLOCK_STEP, 0, BLOCK_STEP-1, BLOCK_STEP-1)
            if prompt is not None:
                self.display.text(prompt, 0, 50, self.foreground_color)
            self.display.show_block()         
        
        if content is not None :
            if self.changed:
                self.clear_window()
                show_prompt(content[self.current_full_page])
                if self.current_full_page == 'calibrate':
                    self.display.calibrate_touch(self.calibration_level)
                self.changed = False            

# --Button----------------------------------------------------------------------------------------->

class ButtonWindow(WindowBase):
    """ Class that builds and runs a main button window"""
    
    # core methods   
    def __init__(self, windows_manager):
        self.type = 'button'
        super().__init__(windows_manager, self.type)

        self.current_field = None
        self.current_zone = None
        self.field = None
        self.zone = None
        self.changed = True
        
    # class interface
        
    def render(self):
        self.state.render(self, self.configs)

    # helper methods                    
    
    def set_touch(self, touch_coordinates):
        """
            Sets the (field, zone) of the touched button (button is a 3 x 3 matrix) 
        """   
        (x, y) = touch_coordinates
        
        self.zone = max(0, min((x - self.column) // ZONE_STEP, 2))
#        self.zone = max(0, min((x % BLOCK_STEP) // ZONE_STEP, 2))
        self.field = max(0, min((y - self.line) // BUTTON_STEP, 2))    
            
        print("x, y: ", x - self.column, y - self.line, "x step: ", ZONE_STEP, "y step: ", BUTTON_STEP )
        print("zone: ", self.zone, " field: ", self.field, "\n")
    
    def check_touch(self):
        """
            Executes actions based on current_page and touched area
            
                      (+/- value, next/last page)
        """
        
        # update current field/zone with lattest touch            
        self.current_field = self.field
        self.current_zone = self.zone
        self.field = None
        self.zone = None
        
        if self.current_field is not None and self.current_zone is not None:
            self.windows_manager.current_window.check_button_touch(self.current_field, self.current_zone)
        
               
    def clear_window(self):
        
        for line in range(BUTTON_BLOCKS_HEIGHT):

            self.display.set_buffer('button')
            
            self.display.set_block(self.column,
                                   self.line + line * FIELD_BLOCK_HEIGHT,
                                   FIELD_BLOCK_WIDTH,
                                   FIELD_BLOCK_HEIGHT)
            self.display.fill(self.background_color)
            self.display.show_block()
            
    def set_highlight(self, color):
        self.highlight_color = color

    # renderers
    def render_window(self, configs=None):
        """Renders arrows and ok button """

#         background_color = self.background_color
#         foreground_color = self.foreground_color
# 
#         # highlight, eventually
#         if isinstance(self.state, FocusedState):
#              background_color = self.highlight_color
#              foreground_color = self.background_color
            
        self.display.set_buffer('button')
        
        #render button
        if self.changed:
            self.clear_window()
            
            # frame button
            for i in range(FIELD_BLOCK_WIDTH):
                self.display.draw_point(self.column + i, self.line, self.foreground_color)
            for j in range(FIELD_BLOCK_HEIGHT * 2):
                self.display.draw_point(self.column, self.line + j, self.foreground_color)

#             print(self.column, self.line, FIELD_BLOCK_WIDTH-1, self.foreground_color)
#             self.display.hline(self.column, self.line, FIELD_BLOCK_WIDTH-1, self.foreground_color)
#             self.display.vline(self.column, self.line, FIELD_BLOCK_HEIGHT * 2 - 1, self.foreground_color)
#             self.display.show_block()

            center_h = int(FIELD_BLOCK_WIDTH / 2) - 8
            center_v = int(FIELD_BLOCK_HEIGHT / 2)
            
            # render icons
            
            #up
            self.display.show_icon("up.bin", self.column + center_h, self.line + 8)
            
            #down
            self.display.show_icon("down.bin", self.column + center_h, self.line + FIELD_BLOCK_HEIGHT * 2 - 24)
            
            #left            
            self.display.show_icon("left.bin", self.column + 8, self.line + FIELD_BLOCK_HEIGHT - 8)
            
            #right            
            self.display.show_icon("right.bin", self.column + FIELD_BLOCK_WIDTH - 24, self.line + FIELD_BLOCK_HEIGHT - 8)
            
            #ok
            self.display.show_icon("ok.bin", self.column + center_h, self.line + FIELD_BLOCK_HEIGHT - 8)                      

            self.changed = False            
                
  
# --Strip----------------------------------------------------------------------------------------->>

class StripWindow(WindowBase):
    """ Class that builds and runs a strip window"""
    
    # core methods   
    def __init__(self, windows_manager):
        self.type = 'strip'
        super().__init__(windows_manager, self.type)
              
        self.minimum = self.configs.minimum_temperature
        self.maximum = self.configs.maximum_temperature
        self.calculate_colors = self.configs.calculate_colors
        self.current_field = None
        self.current_zone = None
        self.field = None
        self.zone = None
        self.text = []
    
    # class interface

    def render(self):
        self.state.render(self, self.configs)

    # helper methods                    
    def set_touch(self, touch_coordinates):  # used to adjust the max and min strip values
        """ Gets the (field, zone) of the touched strip fields
            - a field is a window area (a rectangle with 3 zones: left, middle, right)
            - a touched object is referenced by:  (field_ID,zone_ID), eg. (3,0)
        """   

        (x, y) = touch_coordinates

        # check if touch area is acceptable
        if y > self.line:                   
            self.field = max(0, min(x // BLOCK_STEP, 5))
            self.zone = max(0, min((x % BLOCK_STEP) // ZONE_STEP, 2))

    def check_touch(self):
        """ Executes actions based on page type and touched area

            DO IT!!!
            
        """
        self.current_field = self.field
        self.current_zone = self.zone
        self.field = None
        self.zone = None

    def clear_window(self):

        self.display.set_buffer('bar')
       
        for column in range(STRIP_BLOCKS_WIDTH):             ##  TEM de ser controlado: nr_of_columns é const
            self.display.set_block(self.column + column * FIELD_BLOCK_WIDTH,
                                   self.line ,
                                   FIELD_BLOCK_WIDTH,
                                   FIELD_BLOCK_HEIGHT)
            self.display.fill(self.background_color)
            self.display.show_block()
            
    def set_highlight(self, color):
        self.highlight_color = color

    # renderers
    def render_window(self, configs=None):
        """
            Renders strip window:
                    - text (from data.text)
                    - color temperature scale (heat palette)
        """

        # highlight, eventually
        if isinstance(self.state, FocusedState):
            background_color = self.highlight_color
            text_color = self.background_color
        else:
            background_color = self.background_color
            text_color = self.foreground_color
        
        self.display.set_buffer('strip')
        
        # if there is text in text buffer (eg. a Bar field description)
        if self.data.text:           
            self.text = []
            text_used_blocks = FIELD_BLOCK_WIDTH * STRIP_BLOCKS_WIDTH // len(self.data.text) * 8
            for block in range(STRIP_BLOCKS_WIDTH):
                if block < text_used_blocks:
                    start = block * MAX_FIELD_CHAR
                    finish = start + MAX_FIELD_CHAR -1
                    self.text.append(self.data.text[start: finish + 1])
                else:
                    self.text.append("")
                    
        # else, render color scale: palette Modes (False= min/max input, True=min/max from frame)
        else:
            if self.data.configs.max_min_set:
                self.maximum, self.minimum = self.configs.maximum_temperature, self.configs.minimum_temperature
            else:
                self.maximum, self.minimum = self.data.temperatures['max'], self.data.temperatures['min']
        
        # render all strip blocks            
        for block in range(STRIP_BLOCKS_WIDTH):

            self.display.set_block(block * FIELD_BLOCK_WIDTH, self.line + FIELD_TO_STRIP_DELTA, FIELD_BLOCK_WIDTH-1, FIELD_BLOCK_HEIGHT)
            self.display.fill(background_color)
            if configs:
                self.render_strip_block(configs, block, text_color) 
            self.display.show_block()
  
    def render_strip_block(self, configs, block, text_color):
        """Render a strip block (text or temperature color scale)"""
        
        if self.data.text:           # if there is any text in text buffer (eg. a Bar field description) print it
            self.display.text(self.text[block], 1, 12, text_color)
        
        else:                        # or render color scale
            block_color_range = configs.color_range // 6 if block == 0 or block == 3 else configs.color_range // 3 
            offset_i = BLOCK_STEP // 2 + 12 if block == 0 else 0
            offset_j = 6
            
            strip_pixel_i = (BLOCK_STEP * 3) // configs.color_range - 2
            strip_pixel_j = STRIP_WINDOW_HEIGHT - 20
            
            # Draw color scale pixels
            for i in range(block_color_range):
                color = FrameWindow.get_color(self, i + block * (configs.color_range // 3 - 1), type=1)
                self.display.fill_rect(offset_i + i * strip_pixel_i, offset_j, strip_pixel_i, strip_pixel_j, color)           
            
            # Print max/min temps
            if block == 3:
                self.display.text(f"{self.maximum:.1f}", BLOCK_STEP // 2 , 12, text_color)
            elif block == 0:
                self.display.text(f"{self.minimum:.1f}", 15, 12, text_color)

# --Bar----------------------------------------------------------------------------------------->>>

class BarWindow(WindowBase):
    """ Class that builds and runs a bar window """
    
    # core methods       
    def __init__(self, windows_manager):
        self.type = 'bar'
        super().__init__(windows_manager, self.type)
          
        self.timeout = 1
        self.columns = COLUMNS
        self.current_page = 0
        self.current_field = None
        self.current_zone = None
        self.field = None
        self.zone = None
            
    # class interface


    def render(self):
        self.state.render(self, self.pages)
 
    # helper methods
    
    def set_touch(self, touch_coordinates):   # used to pick and adjust field values and icons
        """ get current field and zone"""

        (x, y) = touch_coordinates
        
        # check if touch area is acceptable 
        if x > self.column:
            self.field = max(0, min(y // FIELD_STEP, 5))
            self.zone = max(0, min((x % BLOCK_STEP) // ZONE_STEP, 2))
    
    def change_page(self, page):
        
        if self.current_zone == 0:           # last page
            self.current_page = page['back']
        elif self.current_zone == 2:         # next page
            self.current_page = page['next']
        else:                                # home page
            self.current_page = 0
            
        if isinstance(self.state, EditState):
            self.set_state(FocusedState())
                    
    def change_field(self, page, field, button_field, button_zone):
        """
            Select field using button arrows and ok
            
            Note: very sensible to calibration
            
        """
        
        # decrease value
        if button_field == 0:
            self.select_field(page, max(0, min(page['value'] - 1, 4)))
         
         # increase value
        elif button_field == 2:
            self.select_field(page, max(0, min(page['value'] + 1, 4)))

    def select_field(self, page, field):
        """
            Set and highlight the selected field in a list
        """
        
        # reset Strip text
        self.data.text = ""
        
        # process field selection for each type
        if page['fields'][field]:
            if page['fields'][field]['type'] == 'menu':
                if page['value'] != field:
                    # select menu
                    page['fields'][page['value']]['highlighted'] = False    # uncheck previous
                    page['fields'][field]['highlighted'] = True             # check current
                    page['value'] = field                                   # set new highlighted menu
                else:                                                   # if doucle touch on selected field, go to selection
                    self.current_page = page['fields'][field]['value']
            elif page['fields'][field]['type'] in ['temperature', 'text', 'radio']:
                # select field - set/reset flags
                page['fields'][field]['highlighted'] = not page['fields'][field]['highlighted'] # toggle choice
                page['value'] = field                                    # set new highlighted field
                if page['fields'][field]['type'] == 'radio':
                    page['fields'][field]['value'] = not page['fields'][field]['value']
                    
            elif page['fields'][field]['type'] in ['knob', 'dropdown']:
                # select field
                page['fields'][page['value']]['highlighted'] = False    # uncheck previous
                page['fields'][field]['highlighted'] = True             # check current
                page['value'] = field                                   # set new highlighted menu
            
            
            # prepare text to show in Strip
            self.data.text = page['fields'][field]['text']

    
    def set_field(self, page, field, button_field, button_zone):
        """
            Set the value of an input field (knob or dorpdown) in editing mode
        
        """
        if page['fields'][field]['value'] is not None:

            if button_zone is not None:
                if isinstance(self.windows_manager.current_window.state, FocusedState):
                    self.windows_manager.current_window.set_state(EditState())
                    
                # decrease value
                if button_zone == 0:           
                    page['fields'][field]['value'] -= page['fields'][field]['delta']
                    
                # quit editing
                elif button_zone == 1:
                    self.windows_manager.current_window.current_page = page['back']
                    self.windows_manager.current_window.set_state(FocusedState())
                 # increase value
                elif button_zone == 2:
                    page['fields'][field]['value'] += page['fields'][field]['delta']
                page['fields'][field]['value'] = max(page['fields'][field]['min'],
                                                 min(page['fields'][field]['value'],
                                                     page['fields'][field]['max']))
            
    def check_touch(self):
        """
            Perform BarWindow touch actions
             - Executes actions based on touched field

        """
        
        self.current_field = self.field
        self.current_zone = self.zone
        self.field = None
        self.zone = None

        page = self.pages[self.current_page]
        

                        
        if self.current_field is not None:
            field = self.current_field-1
            if field < 0:                                # if header touched
                if self.current_zone is not None:
                    # Select page: go to last, next or home page
                    self.change_page(page)
                        
            elif field < 5:                                              # if fields touched
                if page['fields'][field]:
                    # if page is a menu or input
                    self.select_field(page, field)                      
        
#           elif ... for all other cases/types...
        
        if page['subtitle'] == 'Calibrate' and page['value'] == 1:
            self.windows_manager.get_window(Window.FULL).set_current_full_page('calibrate')
            self.current_page = page['back']
            page['value'] = 0
            return True
        
        return False

    def check_button_touch(self, button_field, button_zone):
        """
            Perform ButtonWindow touch actions on BarWindow
             - Executes actions based on button touched field

        """
        
        page = self.pages[self.current_page]     
        field = page['value']

        if field >= 0 and field < 5:
            
            # process page registers based on touched area
            if page['fields'][field]:
                field_type = page['fields'][field]['type']
                # if intput page go to specific page                        
                # menu items: go to its page (in menu or input pages)                              
                if field_type == 'menu':
                    self.change_field(page, field, button_field, button_zone)

                # knobs and dropdown
                elif field_type in ['knob', 'dropdown']:
                    # enter editing mode
                    self.set_field(page, field, button_field, button_zone)    
                # radiobuttons
                elif field_type == 'radio':
                    self.current_page = page['back']   
                # if output page go back home
                if page['type'] == 'output':
                    self.current_page = page['back']
                    
#                elif field_type == 'yyyy': for all other input field cases...
#                elif page['type'] == 'xxxx': for all other page types
        
    def clear_window(self):
        """ clear all pages (bar columns) """

        self.display.set_buffer('bar')
        for column in range(5-self.columns,5):             ##  TEM de ser controlado: nr_of_columns é const
            self.clear_column(column)
            
    def clear_column(self, column):
        """ clear all fields of a page (a bar column) """

        for line in range (BAR_BLOCKS_HEIGHT):
            self.display.set_block(self.column + column * FIELD_BLOCK_WIDTH,
                                   self.line + line * FIELD_BLOCK_HEIGHT,
                                   FIELD_BLOCK_WIDTH,
                                   FIELD_BLOCK_HEIGHT)
            self.display.fill(self.background_color)
            self.display.show_block()

    def set_highlight(self, color):
        self.highlight_color = color
            
    # renderers
    def render_window(self, pages=None):
        """ Renders bar window text and graphic blocks to display """

        self.display.set_buffer('bar')
        
        if pages:
            
            # for all page columns
            for column in range(self.columns):            
            # bar may have 1 to n columns (pages), from right to left   (TO DO: need 2nd current_page and swithcinh!!!)
                if pages[self.current_page]:  
                    self.render_page(pages[self.current_page], column)
                else:
                    self.clear_column(column)
        else:
            self.clear_window()

    def render_page(self, page, column):
        # column index (0-n) is from right to left

        if page:
            # render header
            self.render_header(page, column)
            
            # render fields
            self.render_fields(page, column)
    
    def render_header(self, page, column):
        
        self.display.set_block(self.column + column * FIELD_BLOCK_WIDTH,
                               self.line,
                               FIELD_BLOCK_WIDTH,
                               FIELD_BLOCK_HEIGHT)

        if page['type'] in ['input', 'output']:
            background = self.highlight_color
        else:
            background = self.header_color

        # highlight, eventually
        if isinstance(self.state, FocusedState):
            text_color = background
            background_color = self.background_color
        else:
            text_color = self.background_color
            background_color = background
        
        self.render_field(text_color, f"{page['title']:^12}", 0, background_color, f"{page['subtitle']:^12}", 0)
        self.display.show_block()
                     
    def render_fields(self, page, column):

        line = 1
        for field in page['fields']:
            
            self.display.set_block(self.column + column * FIELD_BLOCK_WIDTH,
                                   self.line + line * FIELD_BLOCK_HEIGHT,
                                   FIELD_BLOCK_WIDTH,
                                   FIELD_BLOCK_HEIGHT + 2)            
            if field:
                if field['active']:
                    if field['highlighted']:                        
                        text_color = self.background_color
                        background_color = self.highlight_color
                    else:
                        text_color = self.foreground_color
                        background_color = self.background_color
                        
                    # menu field
                    if field['type'] == 'menu':
                        self.render_field(text_color, field['name'], 4, background_color)

                    # temperatures output field
                    elif field['type'] == 'temperature':
                        if field['value'] in ['center', 'average', 'max', 'min', 'spot']:
                            self.render_field(text_color, field['name'], 10, background_color, f"{self.data.temperatures[field['value']]:.2f}" + " C", 15)
                        
                    # radio button fields
                    elif field['type'] == 'radio':
                        self.render_field(text_color, field['name'], 10, background_color)

                    # dropdown menu fields
                    elif field['type'] == 'dropdown':
                        ####   Necessita de fazer o rendering em modo de edição (+/-/Enter)
                        self.render_field(text_color, field['name'], 10, background_color, field['list'][field['value']], 10)

                    # knobfields
                    elif field['type'] == 'knob':
                        ####   Necessita de fazer o rendering em modo de edição (+/-/Enter)
                        self.render_field(text_color, field['name'], 10, background_color, f"{field['value']:.2f}", 10)
                    
                    # message fields
                    elif field['type'] == 'message':
                        self.render_field(text_color, field['name'], 10, background_color, field['value'], 10)          

                    # Add more field tpes to render:
                    #   ...
                             
                else:
                    self.display.fill(self.background_color)
            else:
                self.display.fill(self.background_color)
            
            line += 1            
            self.display.show_block()
                    
    def render_field(self, f_color, text_1, tab_1, b_color=None, text_2=None, tab_2=0):
        """
            Generic text field renderer
                prints 2 lines of text on a field
        
        """        
        # clear field
        if b_color is not None:            
            self.display.fill(b_color)
        
        # print 1 or 2 text lines
        self.display.text(text_1, tab_1, 10, f_color)
        if text_2 is not None:
            self.display.text(text_2, tab_2, 25, f_color)

# --Frame----------------------------------------------------------------------------------------->>>>
       
class FrameWindow(WindowBase):
    """ Class that builds a frame window"""
    
    # core methods
    def __init__(self, windows_manager):
        self.type = 'frame'
        super().__init__(windows_manager, self.type)

        self.maximum = self.configs.maximum_temperature
        self.minimum = self.configs.minimum_temperature
        self.delta = self.maximum - self.minimum
        self.calculate_colors = self.configs.calculate_colors
        self.interpolate_pixels =  self.configs.interpolate_pixels
        self._frame_lock = Lock(self.data.frame_lock)
        self.timeout = 1
        self.current_x_pixel, self.current_y_pixel = None, None
        self.x_pixel, self.y_pixel = None, None
        self.pixel_size = FRAME_STEP // 8
        self.x_pixels =  31
        self.y_pixels =  23
        self.block_pixels =  8
        self.spot_index = None
        
    # class interface
   
    def render(self):
        self.state.render(self, self.frame)

    # helper methods
    def get_temperatures(self, frame, index=SOURCE_SIZE):
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
                elif self.spot_index is not None:
                        self.data.temperatures['spot'] = frame[self.spot_index]
            finally:
                self._frame_lock.release()
        else:
            raise Exception("Buffer in use by other process.")
        
    def get_temperature(self, index, frame, interpolate=False):
        """
            Get temperature for pixel referenced by index:
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
        """ Heatmap: returns an RGB565 color representing value """
        
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
            (r,g,b) = self.data.colors.colors[ratio]
        return (r & 0xf8) << 8 | (g & 0xfc) << 3 | b >> 3
    
    def set_touch(self, touch_coordinates):  # used to spot a pixel on frame
        """ Gets the (col, lin) of the touched pixel """
        
        self.pixel_size = FRAME_STEP // 16 if self.interpolate_pixels else FRAME_STEP // 8
        self.x_pixels =  63  if self.interpolate_pixels else 31
        self.y_pixels =  47  if self.interpolate_pixels else 23

        (x, y) = touch_coordinates
        
        # check if touch area is aceptable
        if (x < self.width and y < self.height):
            self.x_pixel =  max(0, min(x // self.pixel_size, self.x_pixels))
            self.y_pixel = max(0, min(y // self.pixel_size, self.y_pixels))

    def check_touch(self):
        """
            Perform touch actions on FrameWindow
                 - Executes actions based touched pixel

        """
        
        self.current_x_pixel = self.x_pixel
        self.current_y_pixel = self.y_pixel
        self.x_pixel = None
        self.y_pixel = None
        
        if self.current_x_pixel is not None and self.current_y_pixel is not None:
            x_step = 48 if self.interpolate_pixels else 24
            y_step = 64 if self.interpolate_pixels else 32
            
            index = self.current_x_pixel + y_step * (x_step - self.current_y_pixel - 1)
            
            self.spot_index = None if index < 0 or index >= x_step*y_step else index

    def check_button_touch(self, button_field, button_zone):
        """
            Perform ButtonWindow touch actions on FrameWindow  
        """
                
        # enter/exit hold state
        if isinstance(self.state, FocusedState):
            self.set_state(HoldState())
            self.data.sensor_running = False                  # NEEDS VALIDATION!!!
            
#         elif isinstance(self.windows_manager.current_window.state, HoldState):
        elif isinstance(self.state, HoldState):
            self.set_state(FocusedState())
            self.data.sensor_running = True                   # NEEDS VALIDATION!!!

    def clear_window(self):        
        self.display.set_buffer('frame')        
        for line in range(FRAME_BLOCKS_HEIGHT):
            for column in range(FRAME_BLOCKS_WIDTH):
                self.clear_block(column, line, self.background_color)
            
    def clear_block(self, column, line, color):
        """ clear all frame blocks """
        self.display.set_block(column * BLOCK_STEP, line * BLOCK_STEP, BLOCK_STEP-1, BLOCK_STEP-1)
        self.display.fill(color)
        self.display.show_block()

    def set_highlight(self, color):
        self.highlight_color = color

    # renderers
    def render_window(self, frame=None):
        """Renders all frame window blocks (temperature plot from sensor) to display"""
        
        # highlight, eventually
        if isinstance(self.state, FocusedState):
            background_color = self.highlight_color
        else:
            background_color = self.background_color
        
        self.block_pixels = 16 if self.interpolate_pixels else 8
        self.pixel_size = FRAME_STEP // 16 if self.interpolate_pixels else FRAME_STEP // 8

        # reset Strip text to allow color scale
        self.data.text = ""


        self.display.set_buffer('frame')
        if frame:
            self.get_temperatures(frame)

            # for all blocks
            for block_j in range(FRAME_BLOCKS_HEIGHT):
                block_y = block_j * FRAME_STEP
                for block_i in range(FRAME_BLOCKS_WIDTH):                
                    block_x = block_i * FRAME_STEP
                    self.display.set_block(block_x, block_y, BLOCK_STEP-1, BLOCK_STEP-1)
                    self.render_frame_block(frame, block_i, block_j, self.interpolate_pixels)
                    self.display.show_block()
        else:
            self.clear_window()

    def render_frame_block(self, frame, block_i, block_j, interpolate=False):
        """ Renders an individual block of a frame """

        j_step = 64 if interpolate else 32
        j_max =  47 if interpolate else 23
        j_offset = self.block_pixels * block_j
        i_offset = self.block_pixels * block_i

        # for all pixels in the block
        for pixel_j in range(self.block_pixels):
            pixel_y = pixel_j * self.pixel_size
            j = j_max - j_offset - pixel_j
            for pixel_i in range(self.block_pixels):
                pixel_x = pixel_i * self.pixel_size
                i = i_offset + pixel_i
                index = i + j * j_step
                color = self.get_color(self.get_temperature(index, frame, interpolate))
                self.display.fill_rect(pixel_x, pixel_y, self.pixel_size,self.pixel_size, color)
                
                # if spot is on, shou pixel contour
                if self.spot_index is not None:
                    if self.spot_index == index:
                        self.display.rect(pixel_x, pixel_y, self.pixel_size,self.pixel_size, self.foreground_color)

# --Manager----------------------------------------------------------------------------------------->>>>>

class WindowManager:
    """ Window Management"""
    
    def __init__(self, windows, display, data):
        self.display = display
        self.data = data
        self.configs = data.configs
        self.windows = []
        self.current_window = None
        self.init_manager(windows)

    def init_manager(self, windows):
        self.create_windows(windows)
        self.set_current_window(self.get_window(Window.FULL))       # initial focus window
        self.current_window.set_state(FocusedState())
        self.current_window.clear()                                 # ????
        
    def add_window(self, window):
        if not isinstance(window, WindowBase):
            raise TypeError("Only WindowBase instances can be added.")
        self.windows.append(window)
        
    def get_windows(self):
        return self.windows
    
    def get_window(self, window=0):
        return self.windows[window]

    def delete_window(self, window):
        result = 0
        try:
            self.windows.remove(window)
            del window
        except ValueError as e:
            print(f"Error: {e}")
            result = -1
        return result
        
    def set_current_window(self, window):
        self.current_window = window
            

    def render(self):
        for window in self.windows:
            self.render_window(window)
                        
    def render_window(self, window):
        window.render()
    
    def touch_window(self, window):
        if window is not None:
            window.touched()
        
    def create_windows(self, windows):
        # Create and register windows in WindowsManager
        for Win in windows:
            window = Win(self)
            self.add_window(window)
    
    def update_windows(self, touched_window):
        if touched_window is not None:
            self.touch_window(touched_window)
        self.render()


# --Input----------------------------------------------------------------------------------------->>>>>>

# Input handling (button or touch)
class InputHandler:
    """ Input processing for the windows """
    
    def __init__(self, windows_manager):
        self.windows_manager = windows_manager
        self.touched_window = windows_manager.current_window
        
    def check_input(self, touch_coordinates, in_operation=True):
        """ callback from touch display
                identifies the touched window and updates the touched window coordinates """
        
        if in_operation:
            # identify window touched and update
            touched_window_type = self.get_touched_window_type(touch_coordinates)
            self.touched_window = self.get_window(touched_window_type)

            # set touched coordinates (i,j) in current window and map to field/zone (Bar/Strip) or x/y (frame) 
            self.touched_window.touch(touch_coordinates)
        else:
            self.touched_window = None
        
    def get_window(self, window_type):
        """ Gets the window object reference from its window type"""
        if self.windows_manager.current_window.type == 'full':
            return self.windows_manager.current_window
            
        for _win in self.windows_manager.windows:
            if _win.type == window_type:
                return _win
    
    def get_touched_window_type(self, touch_coordinates):  # used to identify which window was touched
        """ Gets the label of a touched window """
        
        (x, y) = touch_coordinates
        
        # check touch area            
        if x < FRAME_WINDOW_WIDTH:
            if y < FRAME_WINDOW_HEIGHT:
                return 'frame'
            else:
                return  'strip'
        if y < BAR_WINDOW_HEIGHT:
                return 'bar'
            
        return  'button'

# --Screen----------------------------------------------------------------------------------------->>>>>>>
# The full thing: A complete and functional GUI!

class Screen():
    """ Full Graphics User Interface class"""

#    win = [FullWindow, FrameWindow, BarWindow, StripWindow, ButtonWindow]     # Window to be created and managed
    win = [FullWindow, FrameWindow, BarWindow, StripWindow, ButtonWindow]     # Window to be created and managed
    
    def __init__(self, data_bus):
                
        self.data = data_bus        
        self.display = Display()
        self.windows_manager = WindowManager(self.win, self.display, self.data)
        self.input_handler = InputHandler(self.windows_manager)
        self.display.set_touch(self.input_handler.check_input)                             # touch setup, passing callback

    def loop(self):
        # Main loop
        
        while True:         # Main GUI loop
#            stamp = time.ticks_ms()
            gc.collect()                                   
            self.windows_manager.update_windows(self.input_handler.touched_window)
            gc.collect()                       
#            time.sleep(0.5)
#            print("Gets one screen rendered in %0.4f ms" % (time.ticks_diff(time.ticks_ms(), stamp)))        
#            print("Screen: Used RAM:", gc.mem_alloc(), "Remaining RAM:", gc.mem_free())
            

if __name__=='__main__':
    
    """
        Tests the full GUI:
        
            - Render
                Frame (32 x 24 color matrix)
                Bar (Text, Icons)
                Strip (color scale)
                Button (control)
            - Get touch
                Change state
                Execute action
    """

    
    # setup context

    # create a dummy frame
    frame = [0] * 768
    for j in range(0,24):
        for i in range(0,32):
            frame[i+32*j]= i*j/6

    # stuff data_bus
    from Data import Payload
    data_bus = Payload()
    data_bus.frame = frame
    data_bus.configs.minimum_temperature = 0.0
    data_bus.configs.maximum_temperature = 120.0
    
    # launch windows
    camera = Screen(data_bus)
    camera.loop()
