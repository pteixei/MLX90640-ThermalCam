"""
Thermal camera
================================================================================

Thermal Camera dual threaded software:
- 32x24 temperature matrix acquisition from MLX90640 sensor
- ILI9488 touch display 420x320 for user interface
- "orchestrator"  


* Author(s): Paulo Teixeira


Implementation Notes
--------------------

**Software and Dependencies:**

TODO LIST:
        
- Windows:
    - InputHandler
        - Build all:
            Get touch > Do action
    - FrameWindow
        - loops need some tuneup
        - Zoom
        - Show/Hide Cursor
        - Print Temperatures
    - Bar
        - Field Class with its methods
    

- Data:

    - Need methods to manipulate data
    
        - create methods to manage configs:
            - all configs in a coeherent dataset - a class (storable in flash)

        - create methods to manage status and content:
            - dict with: name, status, values, types, data, positions, colors,... organized into pages, lines, columns
            - aggregate data from all sources (statistics, configs, pico, status)
            - encode mode (show/read), x/y position, navigation (next element)
            - sets a state-machine in main loop for navigation and function runing ( eg, save pic to flash, change mode, etc..)
        
        - Create Generator that yelds content pages

- Systems class with:
    - SD card read/write/list
    - Pico Temperature and Voltage
    - Pico RTC
    - Leds and Buttons
    - Beep
    - Accelerometer/Rotation
    - Sleep/Wake/Shutdown
    
    - Use those methods in Windows
    
ERRORS:

"""

from Sensor import Sensor, RefreshRate
from Windows import Screen, data_bus
import _thread
import time
import gc


def core0_thread():
    """ Core 0: GUI and Navigation
        - GUI: display (ILI9488) driver and graphic tools
            - main loop, status,
                options (menu, views, values)
                actions (frame, bar, configs, warnings, storage)
    """

    # Core 0 starts here

    def StartupData():
        
        global data_bus
        
        configs = data_bus.configs
        configs.minimum_temperature = 25
        configs.maximum_temperature = 35
#         configs.frame_x_offset = 20
#         configs.frame_y_offset = 20
        configs.interpolate_pixels = False
        configs.calculate_colors = False
        configs.max_min_set = True
            
    # initialize settings 
    StartupData()
    
    # launch screen
    screen = Screen()

    # run screen
    screen.loop(data_bus.running)

   # Core 0 ends here

def core1_thread():
    """ Core 1: Sensor and System
        - Sensor: sensor (MLX9060) driver
        - System: system control and monitoring, SD card, leds, buttons
    """
    # Core 1 starts here
  
    global data_bus
  
    def setup_sensor():
        
        if data_bus.configs.interpolate_pixels:
            sensor.refresh_rate = RefreshRate.REFRESH_0_5_HZ
        else:    
            sensor.refresh_rate = RefreshRate.REFRESH_2_HZ
    
    
    # launch sensor
    sensor = Sensor()
    
    # ajust sensor
    setup_sensor()

    # run sensor
    sensor.loop(data_bus.running)
    
    # Core 1 ends here


# Main

data_bus.running = True
second_thread = _thread.start_new_thread(core1_thread, ())
time.sleep_ms(10)
core0_thread()
data_bus.running = False

# Main ends here
