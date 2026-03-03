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

external = coms.Comms()

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
        
        if (offset := external.grove_read()):
            dead = external.deadzone
            static = external.staticflag

            x0, y0 = offset
            x_scale = external.x_adj_factor / 110
            y_scale = external.y_adj_factor / 110

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
                
blink_time = 500
blinking = False

bool_a = False
last_toggle_a= time.ticks_ms()

speaking_flag = False
speaking_timer = 0

while True:
    # Update time 
    now = time.ticks_ms() 
    dt = time.ticks_diff(now, last_time) / 1000.0
    last_time = now
        
    # Grab all pending commands from the ESP
    incoming_commands = external.esp_read()
    
    # Process them one by one
    for data in incoming_commands:
        print(data)
        if data in animation.state_map:
            animation.new_state_flag = True
            animation.current_state = data
            
    if animation.current_state != "idle":
        facetrack() 
        
    # 2. Check if the state changed this frame
    if animation.current_state != animation.previous_state:
        if animation.current_state == "speaking":
            speaking_flag = True
        elif animation.current_state in ["neutral", "idle", "listening"]:
            if speaking_flag:
                print("stop talking (interrupted by new state)")
                speaking_flag = False
                
                # CRITICAL: Snap the mouth closed when speech ends!
                animation.servos["MOU"].set_target(130)
                
    # 3. Speaking timer / animation
    if speaking_flag:
        # Set the mouth position based on the current toggle state
        if bool_a == False:
            animation.servos["MOU"].set_target(130)
        elif bool_a == True:
            animation.servos["MOU"].set_target(70)
            
        # Flip the boolean every 250ms to flap the mouth
        if time.ticks_diff(now, last_toggle_a) >= 250:
            bool_a = not bool_a   # flip the boolean
            last_toggle_a = now


    # Blink mode enabler
    if not blinking and random.randrange(500) == 0: 
        blinking = True
        blink_counter = blink_time
         

        # Calibration mode 
    if (mode.value() == 1):
        animation.current_state = "state_calibrate"
        animation.apply_state("state_calibrate") # change this back to calibrate to keep calibration mode/base for testing
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
            # Blink mode   
            if blinking and animation.current_state != "idle":
                if blink_counter > blink_time - 50:
                    # closed
                    animation.servos["LID"]._write_pwm(30)
                elif blink_counter > 0:
                    # reopen
                    animation.servos["LID"]._write_pwm(110)
                blink_counter -= 1
                if blink_counter == 0:
                    blinking = False
                    
            # Update with whatever state the ESP says
            animation.apply_state(animation.current_state)                   
                
    animation.previous_state = animation.current_state

    # Update all servos except eyelids
    for name, s in servos.items():
        if name == "LID":
            continue
        s.update(dt)
        



