from machine import Pin, PWM
import time

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

        # PERFORMANCE: Precompute inverse of 2*accel to use multiplication instead of division later
        self._inv_2_accel = 1.0 / (2.0 * self.max_accel)

        # limits
        self.min_angle = float(min_angle)
        self.max_angle = float(max_angle)

        # tolerances
        self.pos_tolerance = 0.6
        self.vel_tolerance = 1.0
        
        # PERFORMANCE: Precompute PWM conversion constants to avoid heavy math in the update loop
        # Mapping 0..180 to 500..2500us on a 20000us period, scaled to 65535
        self._pwm_offset = 500.0 * (65535.0 / 20000.0)
        self._pwm_slope = (2000.0 / 180.0) * (65535.0 / 20000.0)

        # debug flag
        self.enabled = enabled

        self._write_pwm(self.pos)

    def set_target(self, angle):
        # Inline clamp to save function call overhead
        angle = float(angle)
        self.target = self.min_angle if angle < self.min_angle else (self.max_angle if angle > self.max_angle else angle)

    def update(self, dt):
        if not self.enabled or dt <= 0:
            return

        error = self.target - self.pos
        dist = abs(error)
        
        desired_dir = 0.0 if dist < 1e-9 else (1.0 if error > 0 else -1.0)
        vel_dir = 0.0 if abs(self.vel) < 1e-9 else (1.0 if self.vel > 0 else -1.0)

        # small-target case
        if dist <= self.pos_tolerance and abs(self.vel) <= self.vel_tolerance:
            self.pos = self.target
            self.vel = 0.0
            self._write_pwm(self.pos)
            return

        # braking-first rule
        if vel_dir != 0 and desired_dir != 0 and vel_dir != desired_dir:
            accel = -vel_dir * self.max_accel
        else:
            # PERFORMANCE: Using precomputed multiplication instead of division
            stopping_dist = (self.vel * self.vel) * self._inv_2_accel 
            if dist > stopping_dist:
                accel = desired_dir * self.max_accel
            else:
                accel = -desired_dir * self.max_accel

        # integrate velocity
        new_vel = self.vel + accel * dt

        # avoid sign flip jitter
        if (self.vel > 0 and new_vel < 0) or (self.vel < 0 and new_vel > 0):
            new_vel = 0.0

        # Inline clamp speed
        self.vel = -self.max_speed if new_vel < -self.max_speed else (self.max_speed if new_vel > self.max_speed else new_vel)

        # integrate position
        self.pos += self.vel * dt

        # Inline clamp position to valid servo range
        self.pos = 0.0 if self.pos < 0.0 else (180.0 if self.pos > 180.0 else self.pos)

        self._write_pwm(self.pos)

    def _write_pwm(self, angle):
        # PERFORMANCE: Single multiplication and addition
        duty = int(self._pwm_offset + self._pwm_slope * angle)
        self.pwm.duty_u16(duty)
