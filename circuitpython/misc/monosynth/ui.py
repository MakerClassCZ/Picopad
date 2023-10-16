import displayio
import terminalio
from digitalio import DigitalInOut, Pull
from adafruit_debouncer import Debouncer
from adafruit_display_shapes.rect import Rect
from adafruit_progressbar.progressbar import HorizontalProgressBar
from adafruit_display_text import label
import adafruit_imageload
import board


def increase(start, step):
    num = start
    while True:
        num += step
        yield num

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
        

    x = 270
    inc = increase(250, -60)
    w = 40
    h = 40
    keys = [
        Rect(x, next(inc), w, h, fill=colors.grey),
        Rect(x, next(inc), w, h, fill=colors.grey),
        Rect(x, next(inc), w, h, fill=colors.grey),
        Rect(x, next(inc), w, h, fill=colors.grey),
    ]


    x = 10
    inc = increase(0, 30)
    labels = [
        label.Label(terminalio.FONT, text="shape", color=colors.red, x=x, y=next(inc)),
        label.Label(terminalio.FONT, text="octave", color=colors.white, x=x, y=next(inc)),
        label.Label(terminalio.FONT, text="lfo", color=colors.white, x=x, y=next(inc)),
        label.Label(terminalio.FONT, text="freqency", color=colors.white, x=x, y=next(inc)),
        label.Label(terminalio.FONT, text="q-factor", color=colors.white, x=x, y=next(inc)),
        label.Label(terminalio.FONT, text="release", color=colors.white, x=x, y=next(inc)),
        label.Label(terminalio.FONT, text="detune", color=colors.white, x=x, y=next(inc)),
    ]

    x = 284
    inc = increase(-30, 60)
    labels_keys = [    
        label.Label(terminalio.FONT, text="G", color=colors.black, x=x, y=next(inc), scale=2),
        label.Label(terminalio.FONT, text="E", color=colors.black, x=x, y=next(inc), scale=2),
        label.Label(terminalio.FONT, text="D", color=colors.black, x=x, y=next(inc), scale=2),
        label.Label(terminalio.FONT, text="C", color=colors.black, x=x, y=next(inc), scale=2),
    ]

    labels = labels + labels_keys

    x = 80
    inc = increase(60, 30)
    w = 150
    h = 8
    bars = [
        HorizontalProgressBar((x, next(inc)), (w, h), bar_color=colors.white,
                            outline_color=colors.light_grey, fill_color=colors.grey,),
        HorizontalProgressBar((x, next(inc)), (w, h), bar_color=colors.white,
                            outline_color=colors.light_grey, fill_color=colors.grey,),
        HorizontalProgressBar((x, next(inc)), (w, h), bar_color=colors.white,
                            outline_color=colors.light_grey, fill_color=colors.grey,),
        HorizontalProgressBar((x, next(inc)), (w, h), bar_color=colors.white,
                            outline_color=colors.light_grey, fill_color=colors.grey,),
        HorizontalProgressBar((x, next(inc)), (w, h), bar_color=colors.white,
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

    x = 80
    w = 15
    h = 13
    for item in range(6):
        sprite = displayio.TileGrid(sprite_sheet, pixel_shader=palette,
                                    width=1,
                                    height=1,
                                    tile_width=w,
                                    tile_height=h)
        sprite.x = x
        sprite.y = 24
        sprite[0] = item
        x += w+10
        sprites.append(sprite)

    x = 80
    for item in range(5):
        sprite = displayio.TileGrid(sprite_sheet, pixel_shader=palette,
                                    width=1,
                                    height=1,
                                    tile_width=w,
                                    tile_height=h)

        sprite.x = x
        sprite.y = 54
        sprite[0] = item + 6
        x += w+10
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

