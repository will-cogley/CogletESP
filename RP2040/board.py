from machine import Pin
import time

from servoclass import Servo


# CogletESP V1.1_3 board pins
MODE_PIN = 20
LED_PIN = 25
SERVO_ENABLE_1_PIN = 10
SERVO_ENABLE_2_PIN = 11

mode = Pin(MODE_PIN, Pin.IN, Pin.PULL_UP)
LED = Pin(LED_PIN, Pin.OUT)

# GP10 / GP11 drive the active-low nOE pins of the two servo output banks.
# Keep both banks disabled while PWM objects are being created.
servo_enable_1 = Pin(SERVO_ENABLE_1_PIN, Pin.OUT, value=1)
servo_enable_2 = Pin(SERVO_ENABLE_2_PIN, Pin.OUT, value=1)


def create_servos():
    """Create Will's original servos using the confirmed physical wiring."""
    return {
        # Left/right are from the robot's own perspective.
        "YAW": Servo(
            pin_num=18,
            max_speed=400,
            max_accel=100,
            min_angle=10,
            max_angle=170,
        ),
        "ROL": Servo(
            pin_num=12,
            max_speed=600,
            max_accel=400,
            min_angle=30,
            max_angle=120,
        ),
        "PIT": Servo(
            pin_num=16,
            max_speed=600,
            max_accel=400,
            min_angle=1,
            max_angle=80,
        ),
        "MOU": Servo(
            pin_num=9,
            max_speed=100000,
            max_accel=3500,
            min_angle=5,
            max_angle=150,
        ),
        "EYL": Servo(
            pin_num=14,
            max_speed=200,
            max_accel=500,
            min_angle=30,
            max_angle=150,
        ),
        "EYR": Servo(
            pin_num=15,
            max_speed=250,
            max_accel=500,
            min_angle=30,
            max_angle=150,
        ),
        "LID": Servo(
            pin_num=8,
            max_speed=100000,
            max_accel=7000,
            min_angle=30,
            max_angle=160,
        ),
        "EAL": Servo(
            pin_num=6,
            max_speed=250,
            max_accel=200,
            min_angle=60,
            max_angle=150,
        ),
        "EAR": Servo(
            pin_num=7,
            max_speed=500,
            max_accel=200,
            min_angle=30,
            max_angle=120,
        ),
    }


def initialize_servos(animation):
    """Run the original staggered startup without changing its behavior."""
    time.sleep(0.5)  # Allow board power to stabilize after boot.

    is_calibrating = mode.value() == 1
    initial_pose = (
        animation.pose_calibrate
        if is_calibrating
        else animation.pose_sleep
    )

    # nOE is active-low.
    servo_enable_1.value(0)
    servo_enable_2.value(0)
    print("Servo banks enabled: GP10=0, GP11=0")

    print("Initiating staggered servo wakeup...")
    for name, servo_obj in animation.servos.items():
        start_angle = initial_pose.get(name, 90)

        servo_obj.pos = start_angle
        servo_obj.target = start_angle
        servo_obj._write_pwm(start_angle)

        delay_ms = 50 if is_calibrating else 250
        time.sleep_ms(delay_ms)

    animation.current_state = (
        "state_calibrate" if is_calibrating else "idle"
    )
    animation.previous_state = animation.current_state
    print("Startup complete.")

    return is_calibrating
