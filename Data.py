"""
Thermal camera
================================================================================

Thermal Camera data_bus:


* Author(s): Paulo Teixeira


Implementation Notes
--------------------

    Aggregates all main shared registers in a central class (Payload)
    
"""

from Sensor import sensor_running, frame_lock, frame
from Colors import Color
from Pages import pages


class Colors():
    # Class that aggregates all color, skin and palette operations
    
    """
        TODO!!!
        
            - move palette and other methods from other modules
            - create changeable skins (set of all colors used in all windows)
        
    """
    
    # A basic range of cold to warm color scale
    colors = ((1, 1, 1), (4, 4, 4), (21, 9, 5), (39, 15, 6), (57, 21, 7), (75, 26, 9),
              (92, 32, 10), (110, 38, 11), (128, 43, 12), (146, 49, 14), (163, 55, 15),
              (181, 60, 16), (199, 66, 18), (217, 72, 19),(217, 78, 28), (199, 85, 44),
              (181, 92, 60), (163, 99, 76), (146, 106, 92), (128, 113, 108), (110, 120, 124),
              (92, 127, 140), (75, 134, 156), (57, 141, 172), (39, 148, 188), (21, 155, 204), (4, 162, 221))  #26 values

    COLORS_RANGE = 26
    
    # color skins
    palette_colors = [
                    {                           # SKIN 1
                    'frame' : {
                            'background' : Color.BLACK,
                            'foreground' : Color.WHITE,
                            'header' : Color.BLUE,
                            'highlight' : Color.YELLOW,
                                },
                    'bar' : {
                            'background' : Color.WHITE,
                            'foreground' : Color.BLACK,
                            'header' : Color.RED,
                            'highlight' : Color.UNITED_NATIONS_BLUE,
                                },
                    'strip' : {
                            'background' : Color.WHITE,
                            'foreground' : Color.BLUE,
                            'header' : Color.RED,
                            'highlight' : Color.UNITED_NATIONS_BLUE,
                                },
                    'button' : {
                            'background' : Color.WHITE,
                            'foreground' : Color.BLACK,
                            'header' : Color.RED,
                            'highlight' : Color.BLUE,
                                },
                    'full' : {
                            'background' : Color.WHITE,
                            'foreground' : Color.BLACK,
                            'header' : Color.RED,
                            'highlight' : Color.BLUE,
                                },
                    },

                    {                           # SKIN 2 # CHANGE THE COLORS BELLOW!!!!
                    'frame' : {
                            'background' : Color.BLACK,
                            'foreground' : Color.WHITE,
                            'header' : Color.BLUE,
                            'highlight' : Color.YELLOW,
                                },
                    'bar' : {
                            'background' : Color.WHITE,
                            'foreground' : Color.BLACK,
                            'header' : Color.RED,
                            'highlight' : Color.UNITED_NATIONS_BLUE,
                                },
                    'strip' : {
                            'background' : Color.WHITE,
                            'foreground' : Color.BLUE,
                            'header' : Color.RED,
                            'highlight' : Color.UNITED_NATIONS_BLUE,
                                },
                    'button' : {
                            'background' : Color.WHITE,
                            'foreground' : Color.BLACK,
                            'header' : Color.RED,
                            'highlight' : Color.BLUE,
                                },
                    'full' : {
                            'background' : Color.WHITE,
                            'foreground' : Color.BLACK,
                            'header' : Color.RED,
                            'highlight' : Color.BLUE,
                                },
                    },
                    ]
    
    def __init__(self):
        
        self.color = Color
        self.skin = 0
        self.window_colors = self.palette_colors[self.skin]
        
    def set_palette(self, palette):
        self.palette = palette
        
    def set_window_colors(self, skin=0):
        self.window_colors = self.palette_colors[skin]    

class Configs():
    # Global Camera Configurations

    def __init__(self, data=pages):

        # Mode
        self.interpolate_pixels = False
        self.calculate_colors = False
        self.step = False
#        self.calibration_level = 2
        self.calibration_level = data[1]['fields'][3]['value']
        
        # Position
        self.frame_x_offset = 0
        self.frame_y_offset = 0
        self.bar_x_offset = 0
        self.bar_y_offset = 0
        self.strip_x_offset = 0
        self.strip_y_offset = 0
        self.button_x_offset = 0
        self.button_y_offset = 0
        
        # Palette
        self.minimum_temperature = 0.0
        self.maximum_temperature = 100.0
        self.temperature_delta = 100.0
        self.max_min_set = False               #if True then get min/max from frame
        self.color_range = Colors.COLORS_RANGE
        self.ink_color = Color.BLACK
        self.paper_color = Color.WHITE
        
    def store(self):
        """ Serializes config data and store it in sd card """
        
        ## TO DO
        pass
    
    def set_temperatures(self, maximum=0.0, minimum=100.0, calculate=True):
        """Sets the temperatures for color palette"""
        
        self.minimum_temperature = maximum
        self.maximum_temperature = minimum
        self.temperature_delta = maximum - minimum
        self.calculate_colors = calculate
        
class Payload():
    # Global Camera data registers
    """
        frame:
            - 32 x 48 temperature (float) from sensor 
        pages:
            - array of Pages:
                 - Page is a dictionary of Fields, with rendering commands and configs
        temperatures:
            - list of temperatures (Average, Center, Min, Max, Spot)
        configs:
            - object with camera's configs
        colors:
            - object with color representation
    """

        
    global frame, sensor_running, frame_lock
    
    def __init__(self):
        
        # registers
        self.frame = frame
        self.pages = pages
        self.temperatures = {'center': 0.0,
                             'average': 0.0,
                             'max': 0.0,
                             'min': 0.0,
                             'spot': 0.0}
        self.colors = Colors()
        self.configs = Configs()
        self.text = ""
        
        # flags
        self.sensor_running = sensor_running
        self.frame_lock = frame_lock
