"""For a detailed guide on all the features of the Circuit Playground Express (cpx) library:
https://adafru.it/cp-made-easy-on-cpx"""
import time
import microcontroller
from adafruit_circuitplayground.express import cpx
from random import random
from math import cos
# Set TONE_PIANO to True to enable a tone piano on the touch pads!
TONE_PIANO = False

# Set this as a float from 0 to 1 to change the brightness. The decimal represents a percentage.
# So, 0.3 means 30% brightness!
cpx.pixels.brightness = 0.1

# Changes to NeoPixel state will not happen without explicitly calling show()
cpx.pixels.auto_write = False


def shuffle(seq):
    return sorted(seq, key=lambda x: random())


def color_wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition red - green - blue - back to red.
    if pos < 0 or pos > 255:
        return (0, 0, 0)
    if pos < 85:
        return (int(255 - pos * 3), int(pos * 3), 0)
    if pos < 170:
        pos -= 85
        return (0, int(255 - pos * 3), int(pos * 3))
    pos -= 170
    return (int(pos * 3), 0, int(255 - (pos * 3)))


color_index = 0
pixel_number = 0

MINUTE = 60
WORK_LENGTH = 25 * MINUTE
BREAK_LENGTH = 8 * MINUTE

# time.monotonic() allows for non-blocking LED animations!
start = time.monotonic()

state_start = start
is_pomo = cpx.switch
pixel_order = shuffle(list(range(10)))
pomo_pixels = [0] * 10
total_pomos = 0

while True:
    old_is_pomo = is_pomo
    is_pomo = cpx.switch
    cpx.pixels.brightness = 0.1

    now = time.monotonic()
    if is_pomo != old_is_pomo:
        # If we change states, then reset linger counter
        state_start = now
        pomo_pixels = [0] * 10
        pixel_order = shuffle(list(range(10)))
        if not is_pomo:
            total_pomos += 1

    linger_time = now - state_start

    if is_pomo:
        # In pomodoro state, we want to slowly fill up with red on all the leds over 25 minutes
        # I want to slowly ooze around the wheel getting gradually more and more red...
        # Probably I ultimately want some kind of perlin-esque distribution
        # with gamma correction

        total_points = int(((255 * 10) / WORK_LENGTH) * linger_time)
    else:
        total_points = int(((255 * 10) / BREAK_LENGTH) * linger_time)

    already_spent = sum(pomo_pixels)
    points_to_distribute = total_points - already_spent
    print(points_to_distribute)
    if not pixel_order:
        # We're over-time so let's flash brightness to remind the human to switch
        # Flash speed is related to how long overtime we have gone
        flash_speed = 60 / (points_to_distribute / 100)  # seconds to flash
        cpx.pixels.brightness = 0.4 * cos(linger_time / flash_speed)
        print(cpx.pixels.brightness)
        cpx.pixels.show()

        continue

    if pomo_pixels[pixel_order[0]] == 255:
        pixel_order.pop(0)

    if not pixel_order:
        continue

    pomo_pixels[pixel_order[0]] += points_to_distribute
    pomo_pixels[pixel_order[0]] = min(pomo_pixels[pixel_order[0]], 255)

    # Draw
    for idx, illumination_value in enumerate(pomo_pixels):
        if is_pomo:
            cpx.pixels[idx] = [illumination_value, 0, 0]
        else:
            cpx.pixels[idx] = [0, illumination_value, 0]

    cpx.pixels.show()

    # If the switch is to the left, it returns True!
    cpx.red_led = cpx.switch

    # Press the buttons to play sounds!
    if cpx.button_a:
        for x in range(total_pomos):
            cpx.play_file("drama.wav")

    elif cpx.button_b:
        for x in range(total_pomos):
            cpx.play_file("low_fade.wav")

    # Set TONE_PIANO to True above to enable a tone piano on the touch pads!
    if TONE_PIANO:
        if cpx.touch_A1:
            cpx.start_tone(262)
        elif cpx.touch_A2:
            cpx.start_tone(294)
        elif cpx.touch_A3:
            cpx.start_tone(330)
        elif cpx.touch_A4:
            cpx.start_tone(349)
        elif cpx.touch_A5:
            cpx.start_tone(392)
        elif cpx.touch_A6:
            cpx.start_tone(440)
        elif cpx.touch_A7:
            cpx.start_tone(494)
        else:
            cpx.stop_tone()
