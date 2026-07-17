# CogletESP RP2040 main loop
import time
import random

import board
import animation
from animation import servos
from coms import Comms
from facetrack import FaceTracker


mode = board.mode
LED = board.LED

LED_oscillator = 25
LED_countdown = LED_oscillator

blink_time = 500
blinking = False

speaking_flag = False
bool_a = False
last_toggle_a = time.ticks_ms()

external = Comms()
face_tracker = FaceTracker(external)

last_time = time.ticks_ms()

# Original staggered startup, now isolated in board.py.
board.initialize_servos(animation)

FTDebug = False  # True isolates the face-tracking code.


while True:
    now = time.ticks_ms()
    dt = time.ticks_diff(now, last_time) / 1000.0
    last_time = now

    if FTDebug == False:
        # Grab every pending state command from the ESP32.
        incoming_commands = external.esp_read()
        for data in incoming_commands:
            if data in animation.state_map:
                animation.new_state_flag = True
                animation.current_state = data

        # Detect state changes.
        if animation.current_state != animation.previous_state:
            if animation.current_state == "speaking":
                speaking_flag = True
            elif animation.current_state in [
                "neutral",
                "idle",
                "listening",
            ]:
                if speaking_flag:
                    speaking_flag = False
                    animation.servos["MOU"].set_target(130)

        # Original 250 ms speaking mouth flap.
        if speaking_flag:
            if bool_a == False:
                animation.servos["MOU"].set_target(130)
            elif bool_a == True:
                animation.servos["MOU"].set_target(70)

            if time.ticks_diff(now, last_toggle_a) >= 250:
                bool_a = not bool_a
                last_toggle_a = now

        # Original random blink trigger.
        if not blinking and random.randrange(500) == 0:
            blinking = True
            blink_counter = blink_time

        # Calibration mode.
        if mode.value() == 1:
            animation.current_state = "state_calibrate"
            animation.apply_state("state_calibrate")
            LED_countdown -= 1
            if LED_countdown <= 0:
                LED.toggle()
                LED_countdown = LED_oscillator
        else:
            if animation.current_state == "idle":
                animation.apply_state("idle")
                animation.servos["LID"]._write_pwm(30)
            else:
                if animation.previous_state == "idle":
                    animation.servos["LID"]._write_pwm(110)
                    animation.servos["PIT"].set_target(10)

                if blinking and animation.current_state != "idle":
                    if blink_counter > blink_time - 50:
                        animation.servos["LID"]._write_pwm(30)
                    elif blink_counter > 0:
                        animation.servos["LID"]._write_pwm(110)

                    blink_counter -= 1
                    if blink_counter == 0:
                        blinking = False

                animation.apply_state(animation.current_state)

        animation.previous_state = animation.current_state
    else:
        animation.servos["LID"]._write_pwm(110)
        animation.current_state = "neutral"

    face_tracker.update()

    # Eyelid is written directly by blink/sleep logic.
    for name, servo in servos.items():
        if name == "LID":
            continue
        servo.update(dt)
