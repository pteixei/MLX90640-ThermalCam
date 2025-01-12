"""
Thermal camera
================================================================================

Thermal Camera Static data



* Author(s): Paulo Teixeira


Implementation Notes
--------------------

    Main constants
    
        - Source size (frame dimension)
        
        - Interpolation constants
            - Uncomment for other sigma values
        
        - Geometric GUI data
        
"""

from Display import BLOCK_STEP, FIELD_STEP, DISPLAY_WIDTH, DISPLAY_HEIGHT

class Window:
    """Enum-like class for window id numbers"""
    FULL = 0
    FRAME = 1
    BAR = 2
    STRIP = 3
    BUTTON = 4


# Core data

SOURCE_SIZE = const(768)

# Interpolation data Kernels

Interpolation_offsets = ((-65, -64 , -1, 0),
                         (-64, -63, 0, 1),
                         (-1, 0, 64, 65),
                         (0, 1, 64, 65))

# sigma=1
P00 = const(0.077847)
P01 = const(0.201164)
P02 = const(0.519827)
# sigma=0.5
#P00 = const(0.024879)
#P01 = const(0.132852)
#P02 = const(0.709417)
# sigma=2
#P00 = const(0.102059)
#P01 = const(0.217408)
#P02 = const(0.463128)

Kernel = ((P00, P01, P01, P02),               
          (P01, P00, P02, P01),
          (P01, P02, P00, P01),
          (P02, P01, P01, P00))

# Graphic objects geometry

# adjustable data:
FRAME_STEP = const(96)      # Frame block "real" step
COLUMNS = const(1)          # Number of Bar columns
FIELD_ZONES = const(3)      # Number of toucheable zones in a field

FIELD_TO_STRIP_DELTA = 8      # (40 - 32)

TEXT_STEP = FIELD_STEP // 2

MAX_FIELD_CHAR = FRAME_STEP // 8

FRAME_BLOCK_WIDTH = FRAME_STEP
FRAME_BLOCK_HEIGHT = FRAME_STEP
FIELD_BLOCK_WIDTH = BLOCK_STEP
FIELD_BLOCK_HEIGHT = FIELD_STEP

FRAME_BLOCKS_WIDTH = 4
FRAME_BLOCKS_HEIGHT = 3
BAR_BLOCKS_WIDTH = COLUMNS
BAR_BLOCKS_HEIGHT = 6
STRIP_BLOCKS_WIDTH = 4
STRIP_BLOCKS_HEIGHT = 1
BUTTON_BLOCKS_WIDTH = 1
BUTTON_BLOCKS_HEIGHT = 2

BUTTON_OFFSET = BAR_BLOCKS_HEIGHT * FIELD_STEP

BUTTON_STEP = FIELD_STEP * BUTTON_BLOCKS_HEIGHT // FIELD_ZONES
ZONE_STEP = BLOCK_STEP // FIELD_ZONES


FRAME_WINDOW_WIDTH = FRAME_BLOCKS_WIDTH * FRAME_BLOCK_WIDTH
FRAME_WINDOW_HEIGHT = FRAME_BLOCKS_HEIGHT * FRAME_BLOCK_HEIGHT
BAR_WINDOW_WIDTH = BAR_BLOCKS_WIDTH * FIELD_BLOCK_WIDTH
BAR_WINDOW_HEIGHT = BAR_BLOCKS_HEIGHT * FIELD_BLOCK_HEIGHT
STRIP_WINDOW_WIDTH = STRIP_BLOCKS_WIDTH * FIELD_BLOCK_WIDTH
STRIP_WINDOW_HEIGHT = STRIP_BLOCKS_HEIGHT * FIELD_BLOCK_HEIGHT 
BUTTON_WINDOW_WIDTH = BUTTON_BLOCKS_WIDTH * FIELD_BLOCK_WIDTH
BUTTON_WINDOW_HEIGHT = BUTTON_BLOCKS_HEIGHT * FIELD_BLOCK_HEIGHT


# Windows geometry

Window_shapes = {
            'frame':
                {'size': (FRAME_WINDOW_WIDTH, FRAME_WINDOW_HEIGHT),
                 'place':(0, 0)},
            'bar':
                {'size': (BAR_WINDOW_WIDTH, BAR_WINDOW_HEIGHT),
                 'place':(DISPLAY_WIDTH - BAR_WINDOW_WIDTH, 0)},
            'strip':
                {'size': (STRIP_WINDOW_WIDTH, STRIP_WINDOW_HEIGHT),
                 'place':(0, DISPLAY_HEIGHT - STRIP_WINDOW_HEIGHT)},
            'button':
                {'size': (BUTTON_WINDOW_WIDTH, BUTTON_WINDOW_HEIGHT),
                 'place':(DISPLAY_WIDTH - BUTTON_WINDOW_WIDTH, DISPLAY_HEIGHT - BUTTON_WINDOW_HEIGHT)},
            'full':
                {'size': (DISPLAY_WIDTH, DISPLAY_HEIGHT),
                 'place':(0, 0)}            
            }
