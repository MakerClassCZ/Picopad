"""
In this example, you will learn how to use the display on your Picopad with displayio library.

We will use the adafruit_display_text library to display text anywhere on the screen.

It requires the adafruit_display_text library placed in /lib directory.
You can find the library in the CircuitPython library bundle (https://circuitpython.org/libraries).
"""

import board
import displayio
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font
import adafruit_imageload
import wifi
import adafruit_ntp
import rtc
import socketpool
import time
import os
import asyncio






# Initialize WiFi
wifi.radio.connect(os.getenv('CIRCUITPY_WIFI_SSID'), os.getenv('CIRCUITPY_WIFI_PASSWORD'))

pool = socketpool.SocketPool(wifi.radio)

# Set up NTP
ntp = adafruit_ntp.NTP(pool, tz_offset=2)
# Set up RTC
rtc.RTC().datetime = ntp.datetime


display = board.DISPLAY

# Create a display group
group = displayio.Group()

bitmap_bg, palette_bg = adafruit_imageload.load("/bg.bmp",
                                          bitmap=displayio.Bitmap,
                                          palette=displayio.Palette)

tile_grid_bg = displayio.TileGrid(bitmap_bg, pixel_shader=palette_bg)

group.append(tile_grid_bg)


bitmap_sun, palette_sun = adafruit_imageload.load("/sun.bmp",
                                          bitmap=displayio.Bitmap,
                                          palette=displayio.Palette)

sun = displayio.TileGrid(bitmap_sun, pixel_shader=palette_sun)

group.append(sun)

sun.x = 150
sun.y = 20

palette_sun.make_transparent(1)


bitmap, palette = adafruit_imageload.load("/fg.bmp",
                                          bitmap=displayio.Bitmap,
                                          palette=displayio.Palette)

palette.make_transparent(7)

# Create a TileGrid to hold the bitmap
tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette)
tile_grid.y = 82
group.append(tile_grid)

# Set the default font for the text
font = bitmap_font.load_font("/Digital-Display-80.bdf")

# Create a text label
text = "00:00:00"
text_area = label.Label(font, text=text, color=0xFFFFFF, scale=1)

# Position the text label
text_area.x = 20
text_area.y = 170

# Add the text label to the display group
group.append(text_area)

# Show the display group
display.root_group = group

async def update_time():
    while True:
        start_time = time.monotonic()
        dt = rtc.RTC().datetime
        date = "%02d:%02d:%02d" %(dt.tm_hour, dt.tm_min, dt.tm_sec)
        text_area.text = date
        end_time = time.monotonic()
        elapsed_time = end_time - start_time

        

        await asyncio.sleep(1 - elapsed_time)


loop = asyncio.get_event_loop()

# Schedule both tasks to run concurrently
loop.run_until_complete(asyncio.gather(
    update_time(),
   
))