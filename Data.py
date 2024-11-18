"""
Thermal camera
================================================================================

Thermal Camera data_bus:



* Author(s): Paulo Teixeira


Implementation Notes
--------------------
"""

from Sensor import running, lock, frame

# Base colors
RED    =   const(0x07E0)
GREEN  =   const(0x001f)
BLUE   =   const(0xf800)
CYAN   =   const(0x07ff)
YELLOW =   const(0xffe0)
WHITE  =   const(0xffff)
BLACK  =   const(0x0000)
GRAY   =   const(0xd69a)

# Page

"""
Page - 
12 pages encode the bar (2x6) and strip (4x1) window fields to be output in their rendering methods
and to be input by touch methods.

TO DO:

- change:
    - bar render (setter) & touch (getter)
        use new encoding (page instead of content)
        make field_render
        max 2 columns
        when 2 columns => frame dont render most right column
    
    - strip render (setter) & touch (getter)
        3 modes:
            scale
            in/out/menu fields
            footer


"""
pages = [
        {'title': "ThermalCam",              # Page 0
        'subtitle': "Home",
         'page_ID': 0,
         'value': 1,
        'type': 'menu',
        'active': True,
        'next': 0,                                          # next page
        'back': 0,                                          # last page
        'fields': [
                {'type': 'menu',      # Field 0
                 'name': "Temperature",
                 'value': True,
                 'text': "Show temperatures",
                 'active': True},
                {'type': 'menu',      # Field 1 
                 'name': "Mode",
                 'value': False,
                 'text': "Select operation mode",
                 'active': True},
                {'type': 'menu',      # Field 2
                 'name': "Settings",
                 'value': False,
                 'text': "Set configurations",
                 'active': True},
                {'type': 'menu',      # Field 3
                 'name': "Card",
                 'value': False,
                 'text': "Save & load frames",
                 'active': True},
                {'type': 'menu',      # Field 4
                 'name': "Off",
                 'value': False,
                 'text': "Power off",
                 'active': True},
                ]
        },
        {'title': "ThermalCam",              # Page 1
        'subtitle': "Settings",
        'page_ID': 1,
        'value': 0,
        'type': 'input',
        'active': True,
        'next': 2,
        'back': 0,
        'fields': [
                {'type': 'radio',            # Field 0
                 'name': "Interpolate",
                 'value': False,
                 'text': "Gaussian interpolatation of pixels",
                 'active': True},
                {'type': 'radio',            # Field 1
                 'name': "Max/Min setup",               # False if strip is fit to min/max from frame; True if min/max is manually set
                 'value': True,
                 'text': "Set max and min temperatures",
                 'active': True},
                {'type': 'radio',            # Field 2
                 'name': "Rotate",
                 'value': True,
                 'text': "Allow screen rotation",
                 'active': True},
                {'type': 'dropdown',             # Field 3
                 'name': "Palette",                     # 0: Calculated; 1: Monochrome Scale, 2-3: Color Scale 1-2,
                 'value': 0,
                 'list': ['0', '1', '2', '3'],
                 'text': "Active palette type",
                 'active': True},
                {},  # Field 4
                {}  # Field 5
                ]
        },
        {'title': "ThermalCam",              # Page 2
        'subtitle': "Settings",
        'page_ID': 2,
        'value': 1,
        'type': 'input',
        'active': True,
        'next': 0,
        'back': 1,
        'fields': [
                {'type': 'dropdown',         # Field 0
                 'name': "Zoom",
                 'value': 1,
                 'list': ['1x', '2x', '4x', '8x'],
                 'text': "Zoom level (1x to 5x)",
                 'active': True},
                {'type': 'knob',            # Field 1
                 'name': "Max temp",               # False if strip is fit to min/max from frame; True if min/max is manually set
                 'value': 0.0,
                 'text': "Maximum temperature",
                 'active': True},
                {'type': 'knob',            # Field 2
                 'name': "Min temp",
                 'value': 100.0,
                 'text': "Minimum temperature",
                 'active': True},
                {},                            # Field 3
                {},                            # Field 4
                {}                             # Field 5
                ]
        },
        {'title': "ThermalCam",              # Page 3
        'subtitle': "Modes",
        'page_ID': 3,
        'value': 1,
        'type': 'input',
        'active': True,
        'next': 0,
        'back': 0,
        'fields': [
                {'type': 'radio',            # Field 0
                 'name': "Capture",
                 'value': True,
                 'text': "Capture mode",
                 'active': True},
                {'type': 'radio',            # Field 1
                 'name': "Frame",            
                 'value': False,
                 'text': "Frame-by-frame mode",
                 'active': True},
                {'type': 'radio',            # Field 2
                 'name': "Temperatures",
                 'value': False,
                 'text': "Show temperatures",
                 'active': True},
                {'type': 'dropdown',            # Field 3
                 'name': "Power",
                 'value': 0,
                 'list': ['0', '1', '2'],
                 'text': "Power mode",
                 'active': True},
                {},                            # Field 4
                {}                             # Field 5
                
                ]
        },
        {'title': "ThermalCam",              # Page 4 - Show Cntr, Avg, Max, Min temps from frame
        'subtitle': "Temperatures",
        'page_ID': 4,
        'value': 0,
        'type': 'output',
        'active': True,
        'next': 0,
        'back': 0,
        'fields': [
                {'type': 'temperature',             # Field 0
                 'name': "Center",
                 'value': 'center',                                     # value is key to data.temperatures{}
                 'text': "Center Temperature",
                 'active': True},
                {'type': 'temperature',            # Field 1
                 'name': "Average",            
                 'value': 'average',
                 'text': "Average Temperature",
                 'active': True},
                {'type': 'temperature',            # Field 2
                 'name': "Max",
                 'value': 'max',
                 'text': "Maximum Temperature",
                 'active': True},
                {'type': 'temperature',            # Field 3
                 'name': "Min",
                 'value': 'min',
                 'text': "Minimum Temperature",
                 'active': True},                 
                {},                                # Field 4
                {'type': 'temperature',            # Field 5
                 'name': "Spot",
                 'value': 'spot',
                 'text': "Spot Temperature",
                 'active': True}           
                ]
        },
        {'title': "ThermalCam",              # Page 5 - Show text messages
        'subtitle': "Message",
        'type': 'output',
        'page_ID': 5,
        'value': 0,
        'active': True,
        'next': 0,
        'back': 0,
        'fields': [
                {'type': 'message',             # Field 0
                 'name': "Warning",
                 'value': 'warning',                                    
                 'text': "Warning",
                 'active': True},
                {'type': 'message',            # Field 1
                 'name': "Notice",            
                 'value': 'notice',
                 'text': "Notice",
                 'active': True},
                {'type': 'message',            # Field 2
                 'name': "Error",
                 'value': 'error',
                 'text': "System error",
                 'active': False},
                {'type': 'message',            # Field 3
                 'name': "Note",
                 'value': 'note',
                 'text': "Note",
                 'active': True},                 
                {},                            # Field 4
                {}                             # Field 5
                ]
        },                                            # Page 6  - SD Card (load, save, list)
       {},                                            # Page 7  - SD Card list (8 lines)
       {},                                            # Page 8 - Strip (mode 0; scale; mode 1: footer)
       {},                                            # Page 9
       {},                                            # Page 10
       {},                                            # Page 11
       {},                                            # Page 12
#         
#         {'title': "Text",              # Page Prototype
#         'subtitle': "Text",
#         'type': 'text',
#         'active': False,
#         'fields': [
#                 {'type': 'text',      # Field Prototype
#                  'name': "Text",
#                  'value': 0,
#                  'text': "Text",
#                  'active': False},
#                 {},
#                 {},
#                 {}
#                 ]
#         },
        ]
CONTENT_PAGES = const (5)               ########   
COLORS_RANGE = const(26)

class Configs():
    # Global Camera Configurations

    def __init__(self):

        # Mode
        self.interpolate_pixels = False
        self.calculate_colors = False
        
        # Position
        self.frame_x_offset = 0
        self.frame_y_offset = 0
        self.bar_x_offset = 0
        self.bar_y_offset = 0
        self.strip_x_offset = 0
        self.strip_y_offset = 8             # (40 - 32)
        
        # Palette
        self.minimum_temperature = 0.0
        self.maximum_temperature = 100.0
        self.temperature_delta = 100.0
        self.max_min_set = False               #if True then get min/max from frame
        self.color_range = COLORS_RANGE
        self.ink_color = BLACK
        self.paper_color = WHITE
    
        
    
    def store(self):
        """ Serializes config data and store it in sd card """
        
        ## TO DO
        pass
    
    def set_palette(self, maximum=0.0, minimum=100.0, calculate=True):
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
        content:
            - array of Pages:
                 - dictionary of Fields
        temperatures:
            - list of temperatures (Average, Center, Min, Max, Spot)
        configs:
            - object with camera's configs
    """

        
    global frame, running, lock
    
    def __init__(self):
    
        self.frame = frame
        self.pages = pages
        self.temperatures = {'center': 0.0,
                             'average': 0.0,
                             'max': 0.0,
                             'min': 0.0,
                             'spot': 0.0}
        self.configs = Configs()
        self.running = running
        self.lock = lock
        
