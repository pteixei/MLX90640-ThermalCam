"""
Thermal camera
================================================================================

Thermal Camera Pages



* Author(s): Paulo Teixeira


Implementation Notes
--------------------

Pages  
    Encode bar (2x6) and strip (4x1) window fields, with content:
        - pages content is rendered and used in touch methods 
        - some fields may store user input data that must be mapped to configs filds
        
           Page Prototype:
        
            {
            'title': "Text",                           
            'subtitle': "Text",
            'page_ID': 0,
            'type': 'text',
            'value': 0,
            'active': False,
            'next': 0,                                # next page
            'back': 0,                                # last page                     
            'fields': [                               # Maximum 5 fields
                    {
                    'type': 'text',                   # Field Prototype
                     'name': "Text",
                     'value': 0,
                     'highlighted': False,
                     'text': "Text",
                     'active': False,
                     },
                    {},
                    {},
                    {}
                    ]
            },


TO DO:

- change:
    - bar pages
        complete
            modes
            settings
            card
        
    - strip pages
        3 types of object to render:
            scale
            in/out/menu fields
            text footer 

"""

pages = [
        {'title': "ThermalCam",                        # Page 0
        'subtitle': "Home",
        'page_ID': 0,
        'value': 0,
        'type': 'menu',
        'active': True,
        'next': 0,                                          # next page
        'back': 0,                                          # last page
        'fields': [
                {'type': 'menu',      # Field 0
                 'name': "Temperature",
                 'highlighted': True,
                 'text': "Show temperatures",
                 'active': True,
                 'value': 4},
                {'type': 'menu',      # Field 1 
                 'name': "Mode",
                 'highlighted': False,
                 'text': "Select operation mode",
                 'active': True,
                 'value': 3},
                {'type': 'menu',      # Field 2
                 'name': "Settings",
                 'highlighted': False,
                 'text': "Set configurations",
                 'active': True,
                 'value': 1},
                {'type': 'menu',      # Field 3
                 'name': "Card",
                 'highlighted': False,
                 'text': "Save & load frames",
                 'active': True,
                 'value': 6},
                {'type': 'menu',      # Field 4
                 'name': "Calibrate",
                 'highlighted': False,
                 'text': "Calibrate Touch Display",
                 'active': True,
                 'value': 10},
                ]
        },
        {'title': "ThermalCam",                       # Page 1
        'subtitle': "Settings",
        'page_ID': 1,
        'value': 0,
        'type': 'input',
        'active': True,
        'next': 2,
        'back': 0,
        'fields': [
                {'type': 'radio',                # Field 0
                 'name': "Interpolate",
                 'highlighted': False,
                 'value': False,
                 'text': "Gaussian interpolatation of pixels",
                 'active': True},
                {'type': 'radio',                # Field 1
                 'name': "Max/Min Temp",         # False if strip is fit to min/max from frame; True if min/max is manually set
                 'highlighted': True,
                 'value': False,
                 'text': "Set max/min scale temperatures",
                 'active': True},
                {'type': 'radio',                # Field 2
                 'name': "Rotate",
                 'highlighted': True,
                 'value': False,
                 'text': "Allow screen rotation",
                 'active': True},
                {'type': 'dropdown',             # Field 3
                 'name': "Cal.level",
                 'highlighted': False,
                 'value': 3,
                 'delta': 1,
                 'max' : 7,
                 'min' : 0,
                 'list': ['0', '1', '2', '3', '4', '5', '6', '7'],                 
                 'text': "Calibration Level",
                 'active': True},
                {'type': 'null',                 # Field 4
                 'name': "",
                 'highlighted': False,
                 'value': None,
                 'text': "",
                 'active': False},      
                ]
        },
        {'title': "ThermalCam",                       # Page 2
        'subtitle': "Settings",
        'page_ID': 2,
        'value': 0,
        'type': 'input',
        'active': True,
        'next': 0,
        'back': 1,
        'fields': [
                {'type': 'dropdown',             # Field 0
                 'name': "Zoom",
                 'highlighted': True,
                 'value': 0,
                 'delta': 1,
                 'max' : 3,
                 'min' : 0,
                 'list': ['1x', '2x', '4x', '8x'],
                 'text': "Zoom level (1x to 5x)",
                 'active': True},
                {'type': 'knob',                 # Field 1
                 'name': "Max temp",
                 'highlighted': False,                 
                 'value': 100.0,
                 'delta': 1.0,
                 'max' : 100.0,
                 'min' : -100.0,
                 'text': "Maximum temperature",
                 'active': True},
                {'type': 'knob',                 # Field 2
                 'name': "Min temp", 
                 'highlighted': False,
                 'value': 1.0,
                 'delta': 1.0,
                 'max' : 100.0,
                 'min' : -100.0,
                 'text': "Minimum temperature",
                 'active': True},
                {'type': 'dropdown',             # Field 3
                 'name': "Palette",                        # 0: Calculated; 1: Monochrome Scale, 2-3: Color Scale 1-2,
                 'highlighted': False,
                 'value': 0,
                 'delta': 1,
                 'max' : 3,
                 'min' : 0,
                 'list': ['0', '1', '2', '3'],
                 'text': "Active palette type",
                 'active': True},
                {'type': 'dropdown',              # Field 4
                 'name': "Brigtness",                     # 0 to 4: dark to bright
                 'highlighted': False,                 
                 'value': 0,
                 'delta': 1,
                 'max' : 4,
                 'min' : 0,
                 'list': ['0', '1', '2', '3', '4'],
                 'text': "LCD Brightness",
                 'active': True}, 
                ]
        },
        {'title': "ThermalCam",                       # Page 3
        'subtitle': "Modes",
        'page_ID': 3,
        'value': 0,
        'type': 'input',
        'active': True,
        'next': 0,
        'back': 0,
        'fields': [
                {'type': 'radio',            # Field 0
                 'name': "Capture",          # Capture mode: continuous and stop/go at touch
                 'highlighted': True,
                 'value': False,
                 'text': "Capture mode",
                 'active': True},
                {'type': 'radio',            # Field 1
                 'name': "Frame",            # Frame mode: continuous 
                 'highlighted': False,
                 'value': False,
                 'text': "Frame-by-frame mode",
                 'active': True},
                {'type': 'radio',            # Field 2
                 'name': "Temperatures",     # Show Temperatures on frame
                 'highlighted': False,
                 'value': False,
                 'text': "Show temperatures",
                 'active': True},
                {'type': 'radio',            # Field 3
                 'name': "Sleep",
                 'highlighted': False,             # True: always on; False: allow sleep/wake
                 'value': False,
                 'text': "Power sleep mode",
                 'active': True},
                {'type': 'null',             # Field 4
                 'name': "",
                 'highlighted': False,
                 'value': None,
                 'text': "",
                 'active': False},           
                ]
        },
        {'title': "ThermalCam",                       # Page 4 - Show Cntr, Avg, Max, Min temps from frame
        'subtitle': "Temperatures",
        'page_ID': 4,
        'value': 0,
        'type': 'output',
        'active': True,
        'next': 0,
        'back': 0,
        'fields': [
                {'type': 'temperature',            # Field 0
                 'name': "Center",
                 'value': 'center',                                     # value is key to data.temperatures{}
                 'text': "Center Temperature",
                 'highlighted': False,
                 'active': True},
                {'type': 'temperature',            # Field 1
                 'name': "Average",            
                 'value': 'average',
                 'text': "Average Temperature",
                 'highlighted': False,
                 'active': True},
                {'type': 'temperature',            # Field 2
                 'name': "Max",
                 'value': 'max',
                 'text': "Maximum Temperature",
                 'highlighted': False,
                 'active': True},
                {'type': 'temperature',            # Field 3
                 'name': "Min",
                 'value': 'min',
                 'text': "Minimum Temperature",
                 'highlighted': False,
                 'active': True},                 
                {'type': 'temperature',            # Field 4
                 'name': "Spot",
                 'value': 'spot',
                 'text': "Spot Temperature",
                 'highlighted': False,
                 'active': True}           
                ]
        },
        {'title': "ThermalCam",                       # Page 5 - Show text messages
        'subtitle': "Message",
        'type': 'output',
        'page_ID': 5,
        'value': 0,
        'active': True,
        'next': 0,
        'back': 0,
        'fields': [
                {'type': 'text',            # Field 0
                 'name': "Warning",
                 'value': 'warning',                                    
                 'text': "Warning",
                 'highlighted': False,
                 'active': True},
                {'type': 'text',            # Field 1
                 'name': "Notice",            
                 'value': 'notice',
                 'text': "Notice",
                 'highlighted': False,
                 'active': True},
                {'type': 'text',            # Field 2
                 'name': "Error",
                 'value': 'error',
                 'text': "System error",
                 'highlighted': False,
                 'active': False},
                {'type': 'text',            # Field 3
                 'name': "Note",
                 'value': 'note',
                 'text': "Note",
                 'highlighted': False,
                 'active': True},                 
                {'type': 'null',                 # Field 4
                 'name': "",
                 'highlighted': False,
                 'value': None,
                 'text': "",
                 'active': False},
                ]
        },
       {'title': "ThermalCam",                        # Page 6  - SD Card action (load, save, list)
        'subtitle': "Card",
        'type': 'menu',
        'page_ID': 6,
        'value': 0,
        'active': True,
        'next': 7,
        'back': 0,
        'fields': [
                {'type': 'menu',            # Field 0
                 'name': "Save",
                 'highlighted': True,
                 'text': "Save current frame",
                 'active': True,
                 'value': 7},
                {'type': 'null',            # Field 1
                 'name': "",
                 'highlighted': False,
                 'value': None,
                 'text': "",
                 'active': False},
                {'type': 'null',            # Field 2
                 'name': "",
                 'highlighted': False,
                 'value': None,
                 'text': "",
                 'active': False}, 
                {'type': 'null',            # Field 3
                 'name': "",
                 'highlighted': False,
                 'value': None,
                 'text': "",
                 'active': False},
                {'type': 'null',            # Field 4
                 'name': "",
                 'highlighted': False,
                 'value': None,
                 'text': "",
                 'active': False},
                ]
        },                                            
       {'title': "ThermalCam",                        # Page 7  - SD Card list (8 lines)
        'subtitle': "Card",
        'type': 'output',
        'page_ID': 6,
        'value': 0,
        'active': True,
        'next': 7,
        'back': 0,
        'fields': [
                {'type': 'null',            # Field 0
                 'name': "",
                 'highlighted': False,
                 'value': None,
                 'text': "",
                 'active': False},
                {'type': 'null',            # Field 1
                 'name': "",
                 'highlighted': False,
                 'value': None,
                 'text': "",
                 'active': False},
                {'type': 'null',            # Field 2
                 'name': "",
                 'highlighted': False,
                 'value': None,
                 'text': "",
                 'active': False}, 
                {'type': 'null',            # Field 3
                 'name': "",
                 'highlighted': False,
                 'value': None,
                 'text': "",
                 'active': False},
                {'type': 'null',            # Field 4
                 'name': "",
                 'highlighted': False,
                 'value': None,
                 'text': "",
                 'active': False},
                ]
        },                                             
       {},                                            # Page 8  - Strip (scale mode)
       {},                                            # Page 9  - Strip (scale footer)
       {'title': "ThermalCam",                        # Page 10  - Touch Calibration
        'subtitle': "Calibrate",
        'type': 'action',
        'page_ID': 10,
        'value': 0,
        'active': True,
        'next': 0,
        'back': 0,
        'fields': [
                {'type': 'null',            # Field 0
                 'name': "",
                 'highlighted': False,
                 'value': None,
                 'text': "",
                 'active': False},
                {'type': 'menu',            # Field 1
                 'name': "Calibrate",
                 'highlighted': True,
                 'text': "Calibrate Screen Touch",
                 'active': True,
                 'value': 10},
                {'type': 'null',            # Field 2
                 'name': "",
                 'highlighted': False,
                 'value': None,
                 'text': "",
                 'active': False}, 
                {'type': 'null',            # Field 3
                 'name': "",
                 'highlighted': False,
                 'value': None,
                 'text': "",
                 'active': False},
                {'type': 'null',            # Field 4
                 'name': "",
                 'highlighted': False,
                 'value': None,
                 'text': "",
                 'active': False},
                ]
        },
       {},                                            # Page 11
        ]
