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
LED = Pin(25, Pin.OUT)

# track direction for each servo (1 = going to max, -1 = going to min)
directions = {name: 1 for name in servos.keys()}

last_time = time.ticks_ms()
last_switch = last_time

animation.servos["YAW"].set_target(90)

yaw_target = 100
yaw_countdown = yaw_target

LED_oscillator = 25
LED_countdown = LED_oscillator

on_time = time.ticks_ms()
startup_sleep = True

def facetrack():
    global yaw_countdown, yaw_target
    if not animation.current_state == "speaking":
        eyl = animation.servos["EYL"]
        eyr = animation.servos["EYR"]
        pit = animation.servos["PIT"]
        yaw = animation.servos["YAW"]
        
        if (offset := coms.grove_read()):
            dead = coms.deadzone
            static = coms.staticflag

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
#                     
        if abs(90 - eyl.target) >= 20:
            yaw_countdown -= 1
            if yaw_countdown <= 0:
                yaw.set_target(90 + ((eyl.target-90)/2))
                yaw_countdown = yaw_target
                
blink_time = 150
blinking = False

while True:
    now = time.ticks_ms()
    dt = time.ticks_diff(now, last_time) / 1000.0
    last_time = now
    
#     print(time.ticks_ms()-on_time)
    
    facetrack()

    if not blinking and random.randrange(500) == 0:
        blinking = True
        blink_counter = blink_time
         
    if (data := coms.ESP_read()):
        print(data)
        animation.new_state_flag = True
        animation.current_state = data
        
    if blinking and animation.current_state != "idle":
        if blink_counter > blink_time - 10:
            # closed
            animation.servos["LID"]._write_pwm(30)
        elif blink_counter > 0:
            # reopen
            animation.servos["LID"]._write_pwm(110)
        blink_counter -= 1
        
        if blink_counter == 0:
            blinking = False
    else:
        if (mode.value() == 1):
            animation.current_state = "state_calibrate"
            animation.apply_state("state_calibrate") # change this back to calibrate to keep calibration mode/base for testing
            
            LED_countdown -= 1
            if LED_countdown <= 0:
                LED.toggle()
                LED_countdown = LED_oscillator
        else:
             animation.apply_state("neutral")
#             animation.apply_state(animation.current_state)
        

    

    for name, s in servos.items():
        if name == "LID":
            continue
        s.update(dt)
        
#     time.sleep_ms(10)
    
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


