"""
In this example, you'll connect Picopad to real world. SD card required!!!

We will use the adafruit_requests library to download teletext page from the https://teletext.ceskatelevize.cz/ and display it on the screen.

The teletext page is png image 320x276 pixels. To display it on the screen, we need to convert it to 4bpp bmp image.
Becouse of limited memory, we will offload the conversion to the teletext.lynt.cz proxy server that convert the image and send it back to us.
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
display.show(group)
bitmap = None

def teletext(page):
        
        global bitmap
        with requests.get("http://teletext.lynt.cz/?page=%s" % (page), stream=True) as resp:
            try:
                prev = int(resp.headers['prev'])
            except:
                prev = page
            try:
                next = int(resp.headers['next'])
            except:
                next = page    

            # Read BMP and DIB headers (54 bytes)
            chunk_size = 18
            data = resp.iter_content(chunk_size=chunk_size).__next__()

            while len(data) < chunk_size:
                add = resp.iter_content(chunk_size=chunk_size-len(data)).__next__()
                data += add

            chunk_size = int.from_bytes(data[14:18], "little") - 4            
            data = resp.iter_content(chunk_size=chunk_size).__next__()

            
            while len(data) < chunk_size:
                add = resp.iter_content(chunk_size=chunk_size-len(data)).__next__()
                data += add
            

            width = int.from_bytes(data[0:4], "little")
            height = int.from_bytes(data[4:8], "little")
            bit_depth = int.from_bytes(data[10:12], "little")
            color_count = 2**bit_depth
            
            line_width_pad = ((width + width % 4) // 8 * bit_depth)

            # Read and process the color palette (64 bytes)
            chunk_size = color_count * bit_depth
            data = resp.iter_content(chunk_size=chunk_size).__next__()

            while len(data) < chunk_size:
                add = resp.iter_content(chunk_size=chunk_size-len(data)).__next__()
                data += add

            print(width, height, bit_depth, color_count)

            palette = displayio.Palette(color_count)
            for i in range(0, len(data), 4):
                blue, green, red, _ = data[i:i+4]
                palette[i//4] = (red << 16) + (green << 8) + blue

            # Process BMP data
            if bitmap is None:
                bitmap = displayio.Bitmap(width, height, color_count)

            row = 1
            chunk_size = line_width_pad

            for data in resp.iter_content(chunk_size=chunk_size):
                index = 0

                #print(row)
                while len(data) < chunk_size:
                    
                    add = resp.iter_content(chunk_size=chunk_size-len(data)).__next__()
                    data += add

                row_offset = (height - row) * width

                for byte in data:
                    pixel1 = byte >> 4
                    pixel2 = byte & 0x0F
                    
                    bitmap[row_offset + index] = pixel1
                    index += 1

                    bitmap[row_offset + index] = pixel2
                    index += 1

                row += 1


        return palette, prev, next

# Download and display first page
palette, prev, next = teletext(page)
group[0] = displayio.TileGrid(bitmap, pixel_shader=palette)
display.refresh()
gc.collect()

while True:
    # Teletext page has resolution 320x276 - we need to scroll down to see the whole page
    if (btn_down.value == False):
        group.y = -40
        display.show(group)
        display.refresh()

    if (btn_up.value == False):
        group.y = 0
        display.show(group)
        display.refresh()

    # Change teletext page
    if (btn_right.value == False):
        palette, prev, next = teletext(next)
        group[0] = displayio.TileGrid(bitmap, pixel_shader=palette)
        display.refresh()
        gc.collect()
    
    if (btn_left.value == False):
        palette, prev, next = teletext(prev)
        group[0] = displayio.TileGrid(bitmap, pixel_shader=palette)
        display.refresh()
        gc.collect()


    if (btn_y.value == False):
        # this is nice alternative to math.ceil()
        # it rounds page to next 10 (eg. from 113 to 120)
        page = int((page + 10)/10)*10
        palette, prev, next = teletext(page)
        group[0] = displayio.TileGrid(bitmap, pixel_shader=palette)
        display.refresh()
        gc.collect()

    if (btn_x.value == False):
        page = int((page)/10)*10
        palette, prev, next = teletext(page)
        group[0] = displayio.TileGrid(bitmap, pixel_shader=palette)
        display.refresh()
        gc.collect()

    if (btn_b.value == False):
        page = int((page + 100)/100)*100
        palette, prev, next = teletext(page)
        group[0] = displayio.TileGrid(bitmap, pixel_shader=palette)
        display.refresh()
        gc.collect()

    if (btn_a.value == False):
        page = int((page)/100)*100
        palette, prev, next = teletext(page)
        group[0] = displayio.TileGrid(bitmap, pixel_shader=palette)
        gc.collect()

