# motion_servo.py  (MicroPython for RP2040)
from machine import Pin, PWM, UART
import time, random
import urandom
from servoclass import Servo
import sys, select, uselect
import math
import animation
import coms
from animation import servos

mode = Pin(20, Pin.IN, Pin.PULL_UP)

# track direction for each servo (1 = going to max, -1 = going to min)
directions = {name: 1 for name in servos.keys()}

last_time = time.ticks_ms()
last_switch = last_time

animation.servos["YAW"].set_target(90)

yaw_target = 100
yaw_countdown = yaw_target

while True:
    now = time.ticks_ms()
    dt = time.ticks_diff(now, last_time) / 1000.0
    last_time = now
    
    if not animation.current_state == "speaking":
        if (offset := coms.grove_read()):
            dead = coms.deadzone
            static = coms.staticflag

            eyl = animation.servos["EYL"]
            eyr = animation.servos["EYR"]
            pit = animation.servos["PIT"]

            x0, y0 = offset
            x_scale = coms.x_adj_factor / 110
            y_scale = coms.y_adj_factor / 110

            if not static:
                if abs(x0) > dead:
                    x = eyl.target + x0 * x_scale
                    eyl.set_target(x)
                    eyr.set_target(x)

                if abs(y0) > dead:
                    y = pit.target + y0 * y_scale
                    pit.set_target(y)
                    
        if abs(90 - animation.servos["EYL"].target) >= 20:
            yaw_countdown -= 1
            if yaw_countdown <= 0:
                animation.servos["YAW"].set_target(90 + ((animation.servos["EYL"].target-90)/2))
                yaw_countdown = yaw_target
        
    if (data := coms.ESP_read()):
        print(data)
        animation.new_state_flag = True
        animation.current_state = data
    
    if (mode.value() == 1):
        animation.apply_pose("pose_base") # change this back to calibrate to keep calibration mode
    else:
        animation.apply_state(animation.current_state)

    for s in servos.values():
        s.update(dt)
#     time.sleep_ms(1)
    
#     # EXAMPLE: randomly trigger a blink
#     if not blink_state["active"] and (random.randint(0, 1000)<1):
#         trigger_blink(servos, now, closed_angle=30, lid="LID")

#     # check if blink should finish
#     update_blink(servos, now, lid="LID")

# blink_state = {
#     "active": False,
#     "start_time": 0,
#     "duration": 150,   # ms lids stay closed
#     "original_pos": None,
# }
# 
# 
# 
# def trigger_blink(servos, now, closed_angle=30, lid="LID"):
#     if blink_state["active"]:
#         return  # already blinking, ignore
#     s = servos["LID"]
#     blink_state["active"] = True
#     blink_state["start_time"] = now
#     blink_state["original_pos"] = s.target  # remember current target
#     s.set_target(s.min_angle)  # snap to closed target
# 
# def update_blink(servos, now, lid="LID"):
#     if blink_state["active"]:
#         if time.ticks_diff(now, blink_state["start_time"]) > blink_state["duration"]:
#             s = servos[lid]
#             s.set_target(blink_state["original_pos"])  # restore old target
#             blink_state["active"] = False

