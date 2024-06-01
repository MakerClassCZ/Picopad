"""
In this example, you'll connect Picopad to real world. SD card required!!!

We will use the adafruit_requests library to download teletext page from the https://teletext.ceskatelevize.cz/ and display it on the screen.

The teletext page is png image 320x276 pixels. To display it on the screen, we need to convert it to 4bpp bmp image.
Becouse of limited memory, we will offload the conversion to the api.makerclass.cz proxy server that convert the image and send it back to us.
For futher memory saving, we will save the image to SD card and display it from there.

We will use buttons to scroll the page up and down and to change the teletext page number.

You can find the required librarie in the CircuitPython library bundle (https://circuitpython.org/libraries).
"""
import adafruit_requests
import socketpool
import wifi
import displayio
import board
import os
import gc
from digitalio import DigitalInOut, Pull

# Setup buttons
btn_down = DigitalInOut(board.SW_DOWN)
# btn_down.direction = Direction.INPUT # - not needed, default is input
btn_down.pull = Pull.UP

btn_up = DigitalInOut(board.SW_UP)
btn_up.pull = Pull.UP

btn_left = DigitalInOut(board.SW_LEFT)
btn_left.pull = Pull.UP

btn_right = DigitalInOut(board.SW_RIGHT)
btn_right.pull = Pull.UP

btn_x = DigitalInOut(board.SW_X)
btn_x.pull = Pull.UP

btn_y = DigitalInOut(board.SW_Y)
btn_y.pull = Pull.UP

btn_a = DigitalInOut(board.SW_A)
btn_a.pull = Pull.UP

btn_b = DigitalInOut(board.SW_B)
btn_b.pull = Pull.UP


# Default teletext page
page = 100

# Initialize WiFi
wifi.radio.connect(os.getenv('CIRCUITPY_WIFI_SSID'), os.getenv('CIRCUITPY_WIFI_PASSWORD'))

pool = socketpool.SocketPool(wifi.radio)
requests = adafruit_requests.Session(pool)

display = board.DISPLAY
display.auto_refresh = False
group = displayio.Group()
group.append(displayio.Group())
display.root_group = group

bitmap = None
palette = None

def teletext(page):

    # We use global palette and bitmap. 
    # It is slower, but prevents memory fragmentation - they have same size for all pages
    global bitmap
    global palette

    with requests.get(f"http://api.makerclass.cz/teletext/getBmp?page={page}", stream=True) as resp:
        # Get headers with previous and next page number
        try:
            prev = int(resp.headers['prev'])
        except:
            prev = page
        try:
            next = int(resp.headers['next'])
        except:
            next = page    

        # Read BMP header and first 4 bytes from DIB header - they contains size of DIB header (14 + 4 bytes)
        chunk_size = 18
        data = b''
        # We use while loop to read the whole chunk, becouse resp.iter_content() can return less bytes than requested
        while len(data) < chunk_size:
            data += resp.iter_content(chunk_size=chunk_size-len(data)).__next__()

        # Read the rest of DIB header (usually 40 bytes - 4 already read)
        # data[14:18] from previous chunk contains size of DIB header
        chunk_size = int.from_bytes(data[14:18], "little") - 4            
        data = b''
        while len(data) < chunk_size:
            data += resp.iter_content(chunk_size=chunk_size-len(data)).__next__()

        # Extract image size and bit depth from DIB header
        width = int.from_bytes(data[0:4], "little")
        height = int.from_bytes(data[4:8], "little")
        bit_depth = int.from_bytes(data[10:12], "little")
        color_count = 2**bit_depth
        
        # BMP row size in bytes must be multiple of 4, so we need to pad it
        line_width_pad = ((width + width % 4) // 8 * bit_depth)

        # Read and process the color palette (64 bytes for 16 colors, 4BPP)
        chunk_size = color_count * bit_depth
        data = b''
        while len(data) < chunk_size:
            data += resp.iter_content(chunk_size=chunk_size-len(data)).__next__()
            
        #print(width, height, bit_depth, color_count)

        if palette is None:
            palette = displayio.Palette(color_count)

        # Extract colors from the palette and convert them from BGR to RGB
        for i in range(0, len(data), 4):
            blue, green, red, _ = data[i:i+4]
            palette[i//4] = (red << 16) + (green << 8) + blue

        if bitmap is None:
            bitmap = displayio.Bitmap(width, height, color_count)

        # Process the image data row by row from bottom to top

        # Row counter
        row = 1
        # We try to load whole row + padding at once
        chunk_size = line_width_pad

        for data in resp.iter_content(chunk_size=chunk_size):
            # pixel position in the row
            index = 0

            while len(data) < chunk_size:
                data += resp.iter_content(chunk_size=chunk_size-len(data)).__next__()

            # Calculate the current row from bottom
            row_offset = (height - row) * width

            # Process every byte returned
            for byte in data:
                # BMP is 4BPP, so every byte contains 2 pixels - we extract them
                pixel1 = byte >> 4
                pixel2 = byte & 0x0F
                
                # Set the pixels in the bitmap
                bitmap[row_offset + index] = pixel1
                index += 1

                bitmap[row_offset + index] = pixel2
                index += 1

            row += 1

    return prev, next

# Download and display first page
prev, next = teletext(page)
group[0] = displayio.TileGrid(bitmap, pixel_shader=palette)
display.refresh()
gc.collect()

while True:
    # Teletext page has resolution 320x276 - we need to scroll down to see the whole page
    if (btn_down.value == False):
        group.y = -40
        display.root_group = group
        display.refresh()

    if (btn_up.value == False):
        group.y = 0
        display.root_group = group
        display.refresh()

    # Change teletext page
    if (btn_right.value == False):
        prev, next = teletext(next)
        #group[0] = displayio.TileGrid(bitmap, pixel_shader=palette)
        display.refresh()
        gc.collect()
    
    if (btn_left.value == False):
        prev, next = teletext(prev)
        #group[0] = displayio.TileGrid(bitmap, pixel_shader=palette)
        display.refresh()
        gc.collect()


    if (btn_y.value == False):
        # this is nice alternative to math.ceil()
        # it rounds page to next 10 (eg. from 113 to 120)
        page = int((page + 10)/10)*10
        prev, next = teletext(page)

        display.refresh()
        gc.collect()

    if (btn_x.value == False):
        page = int((page)/10)*10
        prev, next = teletext(page)

        display.refresh()
        gc.collect()

    if (btn_b.value == False):
        page = int((page + 100)/100)*100
        prev, next = teletext(page)

        display.refresh()
        gc.collect()

    if (btn_a.value == False):
        page = int((page)/100)*100
        prev, next = teletext(page)

        gc.collect()

