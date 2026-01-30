from machine import Pin, PWM
import time, random
import urandom

def clamp(x, a, b):
    return a if x < a else (b if x > b else x)

class Servo:
    def __init__(self, pin_num, max_speed=120.0, max_accel=360.0, min_angle=0.0, max_angle=180.0, enabled=True):
        self.pwm = PWM(Pin(pin_num))
        self.pwm.freq(50)

        # motion state
        self.pos = 90.0
        self.vel = 0.0
        self.target = 90.0

        # tuning
        self.max_speed = float(max_speed)
        self.max_accel = float(max_accel)

        # limits
        self.min_angle = float(min_angle)
        self.max_angle = float(max_angle)

        # tolerances
        self.pos_tolerance = 0.6
        self.vel_tolerance = 1.0
        
        # debug flag
        self.enabled = enabled

        self._write_pwm(self.pos)

    def set_target(self, angle):
        # clamp target to servo’s declared limits
        self.target = clamp(float(angle), self.min_angle, self.max_angle)

    def update(self, dt):
        if not self.enabled:
            return
        if dt <= 0:
            return

        error = self.target - self.pos
        dist = abs(error)
        # direction we need to move to reduce error
        desired_dir = 0 if dist < 1e-9 else (1.0 if error > 0 else -1.0)
        # current velocity sign
        if abs(self.vel) < 1e-9:
            vel_dir = 0.0
        else:
            vel_dir = 1.0 if self.vel > 0 else -1.0

        # small-target case: if we're close & nearly stopped, snap cleanly
        if dist <= self.pos_tolerance and abs(self.vel) <= self.vel_tolerance:
            self.pos = self.target
            self.vel = 0.0
            self._write_pwm(self.pos)
            return

        # braking-first rule: if we're moving opposite desired direction, brake
        if vel_dir != 0 and desired_dir != 0 and vel_dir != desired_dir:
            # apply maximum braking (opposite current velocity)
            accel = -vel_dir * self.max_accel
        else:
            # else decide accelerate or start decelerating so we stop exactly at target
            stopping_dist = (self.vel * self.vel) / (2.0 * self.max_accel)  # always >= 0
            if dist > stopping_dist:
                # still room to accelerate toward the target
                accel = desired_dir * self.max_accel
            else:
                # we must decelerate to stop at the target
                accel = -desired_dir * self.max_accel

        # integrate velocity
        new_vel = self.vel + accel * dt

        # avoid sign flip jitter: if braking would cross zero in this step, clamp to zero
        if self.vel > 0 and new_vel < 0:
            new_vel = 0.0
        elif self.vel < 0 and new_vel > 0:
            new_vel = 0.0

        # clamp speed to limits
        new_vel = clamp(new_vel, -self.max_speed, self.max_speed)

        # integrate position
        self.vel = new_vel
        self.pos = self.pos + self.vel * dt

        # clamp position to valid servo range (avoid writing out-of-bounds)
        self.pos = clamp(self.pos, 0.0, 180.0)

        # final small-check: if we are extremely close, snap to target to avoid tiny oscillation
#         if abs(self.target - self.pos) <= self.pos_tolerance and abs(self.vel) <= self.vel_tolerance:
#             self.pos = self.target
#             self.vel = 0.0

        self._write_pwm(self.pos)

    def _write_pwm(self, angle):
        # map 0..180 -> 500..2500 us pulse width (20 ms period)
        min_us = 500.0
        max_us = 2500.0
        us = min_us + (max_us - min_us) * (angle / 180.0)
        # convert to 16-bit duty for 20 ms period
        duty = int(us * 65535.0 / 20000.0)
        self.pwm.duty_u16(duty)
