# Picopad monosynth - based on @todbot's monosynth1 example
#
# monosynth1_synthio.py -- partial synthio port of 'monosynth1' from mozzi_experiments
# 22 Jun 2023 - @todbot / Tod Kurt
# part of https://github.com/todbot/circuitpython-synthio-tricks

import random
import displayio
import terminalio
import board
import audiomixer
import audiopwmio
import synthio
import ulab.numpy as np
from digitalio import DigitalInOut, Pull
from adafruit_debouncer import Debouncer
from adafruit_display_shapes.rect import Rect
from adafruit_progressbar.progressbar import HorizontalProgressBar
from adafruit_display_text import label
import adafruit_wave
import adafruit_imageload

white = 0xFFFFFF
red = 0xFF0000
blue = 0x0000FF
grey = 0x777777
light_grey = 0xAAAAAA
black = 0x000000
yellow = 0xFFFF00

display = board.DISPLAY
display.auto_refresh = False

group = displayio.Group()

keys = [
    Rect(10, 10, 40, 40, fill=grey),
    Rect(10, 70, 40, 40, fill=grey),
    Rect(10, 130, 40, 40, fill=grey),
    Rect(10, 190, 40, 40, fill=grey),
]

labels = [
    label.Label(terminalio.FONT, text="shape", color=red, x=80, y=30),
    label.Label(terminalio.FONT, text="octave", color=white, x=80, y=60),
    label.Label(terminalio.FONT, text="lfo", color=white, x=80, y=90),
    label.Label(terminalio.FONT, text="freqency", color=white, x=80, y=120),
    label.Label(terminalio.FONT, text="q-factor", color=white, x=80, y=150),
    label.Label(terminalio.FONT, text="release", color=white, x=80, y=180),
    label.Label(terminalio.FONT, text="detune", color=white, x=80, y=210),
    label.Label(terminalio.FONT, text="C", color=black, x=24, y=30, scale=2),
    label.Label(terminalio.FONT, text="D", color=black, x=24, y=90, scale=2),
    label.Label(terminalio.FONT, text="E", color=black, x=24, y=150, scale=2),
    label.Label(terminalio.FONT, text="G", color=black, x=24, y=210, scale=2),
]

bars = [

    HorizontalProgressBar((160, 90), (150, 8), bar_color=white,
                          outline_color=light_grey, fill_color=grey,),
    HorizontalProgressBar((160, 120), (150, 8), bar_color=white,
                          outline_color=light_grey, fill_color=grey,),
    HorizontalProgressBar((160, 150), (150, 8), bar_color=white,
                          outline_color=light_grey, fill_color=grey,),
    HorizontalProgressBar((160, 180), (150, 8), bar_color=white,
                          outline_color=light_grey, fill_color=grey,),
    HorizontalProgressBar((160, 210), (150, 8), bar_color=white,
                          outline_color=light_grey, fill_color=grey,),

]


sprite_sheet, palette = adafruit_imageload.load("/synth.bmp",
                                                bitmap=displayio.Bitmap,
                                                palette=displayio.Palette)

active_palette = displayio.Palette(2)
active_palette[0] = yellow
active_palette[1] = black


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

display.show(group)


# simple range mapper, like Arduino map()
def map_range(s, a1, a2, b1, b2): return b1 + \
    ((s - a1) * (b2 - b1) / (a2 - a1))


def lerp(a, b, t): return (1-t)*a + t*b

def limits(value, plus, lo, hi, loop=False):
    value += plus
    if value < lo:
        if loop:
            return hi
        else:
            return lo
    if value > hi:
        if loop:
            return lo
        else:
            return hi

    return value


class Wavetable:
    """ A 'waveform' for synthio.Note that uses a wavetable w/ a scannable wave position."""

    def __init__(self, filepath, wave_len=256):
        self.w = adafruit_wave.open(filepath)
        self.wave_len = wave_len  # how many samples in each wave
        if self.w.getsampwidth() != 2 or self.w.getnchannels() != 1:
            raise ValueError("unsupported WAV format")
        # empty buffer we'll copy into
        self.waveform = np.zeros(wave_len, dtype=np.int16)
        self.num_waves = self.w.getnframes() // self.wave_len
        self.set_wave_pos(0)

    def set_wave_pos(self, pos):
        """Pick where in wavetable to be, morphing between waves"""
        pos = min(max(pos, 0), self.num_waves-1)  # constrain
        samp_pos = int(pos) * self.wave_len  # get sample position
        self.w.setpos(samp_pos)
        waveA = np.frombuffer(self.w.readframes(self.wave_len), dtype=np.int16)
        self.w.setpos(samp_pos + self.wave_len)  # one wave up
        waveB = np.frombuffer(self.w.readframes(self.wave_len), dtype=np.int16)
        pos_frac = pos - int(pos)  # fractional position between wave A & B
        self.waveform[:] = lerp(waveA, waveB, pos_frac)  # mix waveforms A & B


midi_channel = 1         # which midi channel to receive on
oscs_per_note = 3      # how many oscillators for each note
osc_detune = 0.001     # how much to detune oscillators for phatness
filter_freq_lo = 100   # filter lowest freq
filter_freq_hi = 10000  # filter highest freq
filter_res_lo = 0.5    # filter q lowest value
filter_res_hi = 2.0    # filter q highest value
vibrato_lfo_hi = 0.3   # vibrato amount when modwheel is maxxed out
vibrato_rate = 5       # vibrato frequency


# Setup buttons
buttons = []

for item in [board.SW_LEFT, board.SW_UP, board.SW_DOWN, board.SW_RIGHT, board.SW_A, board.SW_B, board.SW_X, board.SW_Y]:
    pin = DigitalInOut(item)
    pin.pull = Pull.UP
    buttons.append(Debouncer(pin))


notes = [
    60,  # C
    62,  # D
    64,  # E
    67,  # G
]

# set up the audio system, mixer, and synth
audio = audiopwmio.PWMAudioOut(board.D0)  # SCK pin on QTPY RP2040
mixer = audiomixer.Mixer(channel_count=1, sample_rate=28000, buffer_size=2048)
synth = synthio.Synthesizer(channel_count=1, sample_rate=28000)
audio.play(mixer)
mixer.voice[0].play(synth)
mixer.voice[0].level = 0.75  # cut the volume a bit so doesn't distort


VOLUME = 28000
SAMPLE_SIZE = 512
# our oscillator waveform, a 512 sample downward saw wave going from +/-28k
wave_tri = np.concatenate((np.linspace(-VOLUME, VOLUME, num=SAMPLE_SIZE//2, dtype=np.int16),
                          np.linspace(VOLUME, -VOLUME, num=SAMPLE_SIZE//2, dtype=np.int16)))
wave_saw = np.linspace(VOLUME, -VOLUME, num=SAMPLE_SIZE, dtype=np.int16)
wave_squ = np.concatenate((np.ones(SAMPLE_SIZE//2, dtype=np.int16)
                          * VOLUME, np.ones(SAMPLE_SIZE//2, dtype=np.int16)*-VOLUME))
wave_sin = np.array(np.sin(np.linspace(
    0, 4*np.pi, SAMPLE_SIZE, endpoint=False)) * VOLUME, dtype=np.int16)
wave_noise = np.array([random.randint(-VOLUME, VOLUME)
                      for i in range(SAMPLE_SIZE)], dtype=np.int16)
wave_sin_dirty = np.array(wave_sin + (wave_noise/4), dtype=np.int16)

wavetable = Wavetable("PLAITS02.WAV")

# scale set with modwheel
lfo_vibrato = synthio.LFO(rate=vibrato_rate, scale=0.01)


# midi note on
def note_on(notenum, vel):
    amp_level = map_range(vel, 0, 100, 0, 1)
    amp_env = synthio.Envelope(attack_time=0.1, decay_time=0.05,
                               release_time=amp_env_release_time,
                               attack_level=amp_level, sustain_level=amp_level*0.8)
    f = synthio.midi_to_hz(notenum)
    oscs.clear()  # chuck out old oscs to make new ones
    for i in range(oscs_per_note):
        fr = f * (1 + (osc_detune*i))
        lpf = synth.low_pass_filter(filter_freq, filter_res)
        # in synthio, 'Note' objects are more like oscillators
        oscs.append(synthio.Note(frequency=fr, filter=lpf, envelope=amp_env,
                                 waveform=s.shapes[s.shape], bend=lfo_vibrato))
    # press the 'note' (collection of oscs acting in concert)
    synth.press(oscs)

# midi note off


def note_off(notenum, vel):
    synth.release(oscs)
    oscs.clear()


class synh_settings():
    def __init__(self):
        self.shapes = [wave_squ, wave_sin, wave_tri,
                       wave_saw,  wave_noise, wavetable.waveform]
        self.shape = 0
        self.octave = 0
        self.lfo = 0
        self.freq = 30
        self.q = 10
        self.release = 20
        self.detune = 0

        self.current = 0

    def move(self, ch):
        labels[self.current].color = white
        self.current = limits(self.current, 1*ch, 0, 6, True)
        labels[self.current].color = red
        display.refresh()

    def change(self, ch):
        if self.current == 0:
            sprites[self.shape].pixel_shader = palette
            self.shape = limits(self.shape, 1*ch, 0, 5, True)
            sprites[self.shape].pixel_shader = active_palette

        elif self.current == 1:
            sprites[8+self.octave//12].pixel_shader = palette
            self.octave = limits(self.octave, 12*ch, -24, 24)
            sprites[8+self.octave//12
                    ].pixel_shader = active_palette

        elif self.current == 2:
            self.lfo = limits(self.lfo, 10*ch, 0, 100)
            bars[self.current-2].value = self.lfo

        elif self.current == 3:
            self.freq = limits(self.freq, 10*ch, 0, 100)
            bars[self.current-2].value = self.freq

        elif self.current == 4:
            self.q = limits(self.q, 10*ch, 0, 100)
            bars[self.current-2].value = self.q

        elif self.current == 5:
            self.release = limits(self.release, 10*ch, 0, 100)
            bars[self.current-2].value = self.release

        elif self.current == 6:
            self.detune = limits(self.detune, 10*ch, 0, 100)
            bars[self.current-2].value = self.detune

        display.refresh()


s = synh_settings()

oscs = []   # holds currently sounding oscillators
filter_freq = s.freq  # current setting of filter
filter_res = s.q   # current setting of filter
amp_env_release_time = s.release  # current release time
note_played = 0  # current note playing

bars[0].value = s.lfo
bars[1].value = s.freq
bars[2].value = s.q
bars[3].value = s.release
bars[4].value = s.detune

velocity = 100
last = 0

display.refresh()


while True:
    for item in buttons:
        item.update()

    # to do global filtermod we must iterate over all oscillators in each note
    for osc in oscs:
        osc.filter = synth.low_pass_filter(filter_freq, filter_res)

    for item in range(4):

        if (buttons[item].fell):
            note = notes[item]+s.octave
            note_off(note_played, 0)
            note_on(note, velocity)
            note_played = note
            keys[item].fill = white
            display.refresh()

        if (buttons[item].rose):
            note = notes[item]+s.octave
            note_off(note, 0)
            keys[item].fill = grey
            display.refresh()

    if (buttons[4].fell):
        s.change(-1)

    if (buttons[5].fell):
        s.change(1)

    if (buttons[6].fell):
        s.move(-1)

    if (buttons[7].fell):
        s.move(1)

    lfo_vibrato.scale = map_range(s.lfo, 0, 100, 0, vibrato_lfo_hi)
    filter_freq = map_range(s.freq, 0, 100, filter_freq_lo, filter_freq_hi)
    filter_res = map_range(s.q, 0, 100, filter_res_lo, filter_res_hi)
    amp_env_release_time = map_range(s.release, 0, 100, 0.1, 1)
    osc_detune = map_range(s.detune, 0, 100, 0, 0.01)

    # debug
    if lfo_vibrato.scale + filter_freq + filter_res + amp_env_release_time + osc_detune != last:
        print(s.shape, s.octave, s.lfo, s.freq, s.q, s.release, s.detune)
        print(lfo_vibrato.scale, filter_freq, filter_res,
              amp_env_release_time, osc_detune)
    last = lfo_vibrato.scale + filter_freq + \
        filter_res + amp_env_release_time + osc_detune
