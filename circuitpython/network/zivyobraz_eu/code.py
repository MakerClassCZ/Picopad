
import displayio
import wifi
import socketpool
import adafruit_requests
import os
import time
import alarm
import board
import gc

# Init display
display = board.DISPLAY
display.auto_refresh = False

# Connect to WiFi
wifi.radio.connect(os.getenv('CIRCUITPY_WIFI_SSID'), os.getenv('CIRCUITPY_WIFI_PASSWORD'))
pool = socketpool.SocketPool(wifi.radio)
requests = adafruit_requests.Session(pool)

mac_addr = ":".join([f"{i:02x}" for i in wifi.radio.mac_address])

def process_zivyobraz(url):
    resp = requests.get(url, stream=True)

    # Get headers
    try:
        sleep_time = int(resp.headers['sleep'])*60
       
    except:
        sleep_time = 60*60
   
    # Read BMP and DIB headers (54 bytes)
    chunk_size = 54
    headers = resp.iter_content(chunk_size=chunk_size).__next__()

    while len(headers) < chunk_size:
        add = resp.iter_content(chunk_size=chunk_size-len(headers)).__next__()
        headers += add
    width = int.from_bytes(headers[18:22], "little")
    height = int.from_bytes(headers[22:26], "little")
    bit_depth = int.from_bytes(headers[28:30], "little")
    color_count = 2**bit_depth
    
    line_width_pad = ((width + width % 4) // 8 * bit_depth)
    
    # Read and process the color palette (64 bytes)
    chunk_size = color_count * bit_depth
    palette_data = resp.iter_content(chunk_size=chunk_size).__next__()

    while len(palette_data) < chunk_size:
        add = resp.iter_content(chunk_size=chunk_size-len(palette_data)).__next__()
        palette_data += add

    #print(width, height, bit_depth, color_count)

    palette = displayio.Palette(color_count)
    for i in range(0, len(palette_data), 4):
        blue, green, red, _ = palette_data[i:i+4]
        palette[i//4] = (red << 16) + (green << 8) + blue

    # Process BMP data
    bitmap = displayio.Bitmap(width, height, color_count)

    row = 1
    chunk_size = line_width_pad

    for chunk in resp.iter_content(chunk_size=chunk_size):
        index = 0
        
        while len(chunk) < chunk_size:
            add = resp.iter_content(chunk_size=chunk_size-len(chunk)).__next__()
            chunk += add

        row_offset = (height - row) * width

        for byte in chunk:
            pixel1 = byte >> 4
            pixel2 = byte & 0x0F
            
            bitmap[row_offset + index] = pixel1
            index += 1

            bitmap[row_offset + index] = pixel2
            index += 1

        row += 1 

    resp.close()
    gc.collect()
    return bitmap, palette, sleep_time


URL = f"http://cdn.zivyobraz.eu/index.php?mac={mac_addr}&x={display.width}&y={display.height}&c=7C&fw=1"

group = displayio.Group()
group.append(displayio.Group())
display.show(group)

while True:
    bitmap, palette, sleep_time = process_zivyobraz(URL)
    group[0] = displayio.TileGrid(bitmap, pixel_shader=palette)
    display.refresh()
    time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + sleep_time)
    alarm.light_sleep_until_alarms(time_alarm)
    