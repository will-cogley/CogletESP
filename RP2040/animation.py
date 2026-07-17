import time

import board
from poses import (
    pose_calibrate,
    pose_sleep,
    pose_base,
    pose_speaking,
    pose_stop_speaking,
    pose_thinking_1,
    pose_curious_2,
    pose_map,
)


current_pose = "pose_base"
current_state = "state_startup"
previous_state = None
animation_bool_a = False
animation_bool_b = False
last_toggle_a = time.ticks_ms()
last_toggle_b = time.ticks_ms()
new_state_flag = False


# Physical pins and servo dynamics live in board.py.
servos = board.create_servos()


def apply_pose(pose):
    pose = pose_map.get(pose, pose_calibrate)
    for name, angle in pose.items():
        if name in servos:
            servos[name].set_target(angle)


def apply_state(state_name):
    state_func = state_map.get(state_name)
    if state_func:
        state_func()
    else:
        print(f"Unknown state: {state_name}")


#_________________# States (Mix of poses + animations) #_________________#



def state_startup():
    global new_state_flag
    if new_state_flag == True:
        apply_pose("pose_calibrate")
        new_state_flag = False
        
def state_calibrate():
    global new_state_flag
#     if new_state_flag == True:
    apply_pose("pose_calibrate")
    new_state_flag = False

def state_sleep():
    global new_state_flag
    if new_state_flag == True:
        apply_pose("pose_sleep")
        new_state_flag = False
        
def state_speaking():
    global new_state_flag
    if new_state_flag == True:
        apply_pose("pose_speaking")
        new_state_flag = False
#     if animation_bool_a == False:
#         servos["MOU"].set_target(130)
#     if animation_bool_a == True:
#         servos["MOU"].set_target(10)
#     if time.ticks_diff(now, last_toggle_a) >= 300:
#         animation_bool_a = not animation_bool_a   # flip the boolean
#         last_toggle_a = now

def state_thinking():
    now=time.ticks_ms()
    global animation_bool_a, last_toggle_a, animation_bool_b, last_toggle_b, new_state_flag
    if new_state_flag == True:
        apply_pose("pose_base")
        new_state_flag = False
    if animation_bool_a == False:
        servos["PIT"].set_target(50)
    if animation_bool_a == True:
        servos["PIT"].set_target(120)
    if time.ticks_diff(now, last_toggle_a) >= 700:
        animation_bool_a = not animation_bool_a   # flip the boolean
        last_toggle_a = now
        
        
def state_listen():
    global new_state_flag
    if new_state_flag == True:
        apply_pose("pose_curious_2")
        new_state_flag = False
        
def state_neutral():
    global new_state_flag
    if new_state_flag == True:
        apply_pose("pose_stop_speaking")
        new_state_flag = False
        
def state_happy():
    now=time.ticks_ms()
    global animation_bool_a, last_toggle_a, animation_bool_b, last_toggle_b, new_state_flag
    if new_state_flag == True:
        apply_pose("pose_base")
        new_state_flag = False
#     print("idle")
    if animation_bool_a == False:
        servos["ROL"].set_target(70)
    if animation_bool_a == True:
        servos["ROL"].set_target(110)
    if time.ticks_diff(now, last_toggle_a) >= 2000:
        animation_bool_a = not animation_bool_a   # flip the boolean
        last_toggle_a = now
        
    if animation_bool_b == False:
        servos["EAL"].set_target(100)
        servos["EAR"].set_target(60)
    if animation_bool_b == True:
        servos["EAL"].set_target(160)
        servos["EAR"].set_target(120)
    if time.ticks_diff(now, last_toggle_b) >= 1000:
        animation_bool_b = not animation_bool_b   # flip the boolean
        last_toggle_b = now
#         print("Toggled:", animation_bool_a)        

def state_limber_up():
    now=time.ticks_ms()
    global animation_bool_a, last_toggle_a, animation_bool_b, last_toggle_b, new_state_flag
    if new_state_flag == True:
        apply_pose("pose_base")
        new_state_flag = False
#     print("idle")
    if animation_bool_a == False:
#         servos["YAW"].set_target(50)
        servos["ROL"].set_target(70)
        servos["PIT"].set_target(70)
        servos["EAL"].set_target(100)
        servos["EYL"].set_target(60)
        servos["MOU"].set_target(20)
        servos["LID"].set_target(20)
        servos["EYR"].set_target(60)
        servos["EAL"].set_target(60)
        servos["EAR"].set_target(60)
    if animation_bool_a == True:
#         servos["YAW"].set_target(130)
        servos["ROL"].set_target(110)
        servos["PIT"].set_target(5)
        servos["EAL"].set_target(160)
        servos["EYL"].set_target(120)
        servos["MOU"].set_target(160)
        servos["LID"].set_target(160)
        servos["EYR"].set_target(120)
        servos["EAL"].set_target(120)
        servos["EAR"].set_target(120)
    if time.ticks_diff(now, last_toggle_a) >= 1000:
        animation_bool_a = not animation_bool_a   # flip the boolean
        last_toggle_a = now
        
# Note: system states:
#   - idle: sleeping, wakeword not initiated listening mode
#   - neutral: between finished speaking and begun listening. potentially use as marker for end of speech
#   - listening
#   - speaking
        
state_map={  
    "neutral": state_neutral,
    "idle": state_sleep,
    "listening": state_listen,
    "state_startup": state_startup,
    "thinking": state_thinking,
    "speaking": state_speaking,
    "state_limber_up": state_limber_up,
    "happy": state_happy,
    "state_calibrate": state_calibrate
}

#_________________#  #_________________#            





