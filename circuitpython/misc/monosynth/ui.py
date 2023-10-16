import displayio
import terminalio
from digitalio import DigitalInOut, Pull
from adafruit_debouncer import Debouncer
from adafruit_display_shapes.rect import Rect
from adafruit_progressbar.progressbar import HorizontalProgressBar
from adafruit_display_text import label
import adafruit_imageload
import board

def get_display():
    
    display = board.DISPLAY
    display.auto_refresh = False
    group = displayio.Group()

    class colors:
        white = 0xFFFFFF
        red = 0xFF0000
        grey = 0x777777
        light_grey = 0xAAAAAA
        black = 0x000000
        yellow = 0xFFFF00
        


    keys = [
        Rect(10, 10, 40, 40, fill=colors.grey),
        Rect(10, 70, 40, 40, fill=colors.grey),
        Rect(10, 130, 40, 40, fill=colors.grey),
        Rect(10, 190, 40, 40, fill=colors.grey),
    ]

    labels = [
        label.Label(terminalio.FONT, text="shape", color=colors.red, x=80, y=30),
        label.Label(terminalio.FONT, text="octave", color=colors.white, x=80, y=60),
        label.Label(terminalio.FONT, text="lfo", color=colors.white, x=80, y=90),
        label.Label(terminalio.FONT, text="freqency", color=colors.white, x=80, y=120),
        label.Label(terminalio.FONT, text="q-factor", color=colors.white, x=80, y=150),
        label.Label(terminalio.FONT, text="release", color=colors.white, x=80, y=180),
        label.Label(terminalio.FONT, text="detune", color=colors.white, x=80, y=210),
        label.Label(terminalio.FONT, text="C", color=colors.black, x=24, y=30, scale=2),
        label.Label(terminalio.FONT, text="D", color=colors.black, x=24, y=90, scale=2),
        label.Label(terminalio.FONT, text="E", color=colors.black, x=24, y=150, scale=2),
        label.Label(terminalio.FONT, text="G", color=colors.black, x=24, y=210, scale=2),
    ]

    bars = [

        HorizontalProgressBar((160, 90), (150, 8), bar_color=colors.white,
                            outline_color=colors.light_grey, fill_color=colors.grey,),
        HorizontalProgressBar((160, 120), (150, 8), bar_color=colors.white,
                            outline_color=colors.light_grey, fill_color=colors.grey,),
        HorizontalProgressBar((160, 150), (150, 8), bar_color=colors.white,
                            outline_color=colors.light_grey, fill_color=colors.grey,),
        HorizontalProgressBar((160, 180), (150, 8), bar_color=colors.white,
                            outline_color=colors.light_grey, fill_color=colors.grey,),
        HorizontalProgressBar((160, 210), (150, 8), bar_color=colors.white,
                            outline_color=colors.light_grey, fill_color=colors.grey,),

    ]


    sprite_sheet, palette = adafruit_imageload.load("/synth.bmp",
                                                    bitmap=displayio.Bitmap,
                                                    palette=displayio.Palette)

    active_palette = displayio.Palette(2)
    active_palette[0] = colors.yellow
    active_palette[1] = colors.black

    class palettes:
        normal = palette
        active = active_palette


    sprites = []

    pos = 160
    for item in range(6):
        sprite = displayio.TileGrid(sprite_sheet, pixel_shader=palette,
                                    width=1,
                                    height=1,
                                    tile_width=15,
                                    tile_height=13)

        sprite.x = pos
        sprite.y = 24
        sprite[0] = item
        pos += 25
        sprites.append(sprite)

    pos = 160
    for item in range(5):
        sprite = displayio.TileGrid(sprite_sheet, pixel_shader=palette,
                                    width=1,
                                    height=1,
                                    tile_width=15,
                                    tile_height=13)

        sprite.x = pos
        sprite.y = 54
        sprite[0] = item + 6
        pos += 25
        sprites.append(sprite)

    sprites[0].pixel_shader = active_palette
    sprites[8].pixel_shader = active_palette

    for item in keys + labels + bars + sprites:
        group.append(item)

    # Setup buttons
    buttons = []

    for item in [ board.SW_A, board.SW_B, board.SW_X, board.SW_Y,
                  board.SW_LEFT, board.SW_RIGHT, board.SW_UP, board.SW_DOWN ]:
        pin = DigitalInOut(item)
        pin.pull = Pull.UP
        buttons.append(Debouncer(pin))


    display.show(group)

    return display, keys, labels, bars, sprites, buttons, colors, palettes

