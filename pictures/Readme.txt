ICON creation

1. Use paint to create PNG with correct shape and dimensions
   Icons: 16 x 16
   Sprites: 96 x 40

2. PNG files with sprites and icons are transformed into an RGB 
text comma separated framebuffer file: <file_name>.txt (0, 12, 21...) 
    use tools online (eg. https://onlinepngtools.com/convert-png-to-rgb-values or any other)
    may need extra step, or may be skiped if online tool generate .bin
(1 byte per base color) 

3. Script "convert text to bin.py" reads <file_name>.txt and 
converts it to an RGB BIN file <file_name>.bin and a RGB565 BIN file
    may need adaptation (filenames and path, image size, extra convertions, etc.)

4. Download TXT files and "convert text to bin-pico.py" to 
RPi pico and run it