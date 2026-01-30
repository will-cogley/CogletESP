# motion_servo.py  (MicroPython for RP2040)
from machine import Pin, PWM, UART
import time, random
import urandom
from servoclass import Servo
import sys, select, uselect
import math
import animation
from animation import servos

ESP = UART(1, baudrate=115200, tx=Pin(4), rx=Pin(5))
rx_buffer = b""

mode = Pin(20, Pin.IN, Pin.PULL_UP)

# track direction for each servo (1 = going to max, -1 = going to min)
directions = {name: 1 for name in servos.keys()}

last_time = time.ticks_ms()
last_switch = last_time

# servos["YAW"].set_target(88)
# # servos["RWH"].set_target(89)


while True:
    now = time.ticks_ms()
    dt = time.ticks_diff(now, last_time) / 1000.0
    last_time = now
    
#     # check if blink should finish
#     update_blink(servos, now, lid="LID")
    
    if ESP.any():
        rx_buffer += ESP.read()   # bytes + bytes = OK
        while b"\n" in rx_buffer:
            line, rx_buffer = rx_buffer.split(b"\n", 1)
            rcvstate = line.decode().strip()
            print("RX:", rcvstate)
            if rcvstate in animation.state_map:
                animation.apply_pose(rcvstate)
                
                
#                 print("recognised")
    
#     if (mode.value() == 0):
#         animation.apply_state("state_limber_up")

    if (mode.value() == 1):
        animation.apply_pose("pose_calibrate")

    for s in servos.values():
        s.update(dt)
    time.sleep_ms(1)
    
#     # EXAMPLE: randomly trigger a blink
#     if not blink_state["active"] and (random.randint(0, 1000)<1):
#         trigger_blink(servos, now, closed_angle=30, lid="LID")

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
