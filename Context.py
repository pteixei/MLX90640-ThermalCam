"""
        Content
        - Each content register has:
            - type: (text, icon)
            - content: (labels, registers, prompts)
            - location: field/sub-field
            - action: (show field, get touch, flash field)
"""


global content

# Refazer content (no âmbito da classe Context() com um generator que dá , para determinada página, "next" content!)
#  -Content está organizado em "pages" (colunas) e "fields" (linhas) com formatação dos campos de Bar
#  -Content é O REGISTO de configs, temperatures e de current_state!!!
#

content = [[                                                  # page 0 - Global Settings
            {'Title': "Settings",
            'Subtitle': "Modes"},            
            {'Calculate': True,
            'Interpolate': True},
            {'Max_Min_set': False,    # Max_Min is False if strip is fit to min/max from fram; is True if min/max is manually set
             'Rotate': False,
#            'Warning': "Battery Low",
#            'Notice': "Save pic",
            },
            {'Title': "Settings",
            'Subtitle': "Configs",
            'Capture': False,
            'Interpolate': True,
#            'Warning': "Battery Low",
#            'Notice': "Save pic",
            },
            {'Title': "SD Drive",
            'Subtitle': "Read-Write"},
            {'Capture': False,
            'Interpolate': True
#            'Warning': "Battery Low",
#            'Notice': "Save pic",
            }, {}
            ],[                                                # page 1 - ...
                {}, {}, {}, {}, {}, {}
            ],[                                                # page 2 - ...
                {}, {}, {}, {}, {}, {}
            ],[                                                # page 3 - Temperatures
            {'Title': "Camera",
            'Subtitle': "Temperature"},
            {}, {}, {}, {}
#            {'Center':f"{temperatures[0]:.2f}" + " C"},
#            {'Average':f"{temperatures[1]:.2f}" + " C"},
#            {'Max':f"{temperatures[2]:.2f}" + " C"},
#            {'Min':f"{temperatures[3]:.2f}" + " C"},
#            {'Spot':f"{temperatures[4]:.2f}" + " C"},
#            {'Warning': "Battery Low"},
#            {'Notice': "Save pic"}
            ],[                                                # page 4 - Menus                
            {'Title': "Themal Cam",
            'Subtitle': "Menu"},
            {},
            {'Camera': True},
            {'Media': False},
            {'Mode': False},
            {'Setting': False},
            ]]

CONTENT_PAGES = const (5)