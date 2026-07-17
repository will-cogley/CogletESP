import animation


class FaceTracker:
    """Will's original Grove-to-eye/head tracking behavior."""

    def __init__(self, external):
        self.external = external
        self.yaw_target = 100
        self.yaw_countdown = self.yaw_target

    def update(self):
        # Always read the sensor to prevent serial buffer overflows.
        offset = self.external.grove_read()

        # Only move the servos while the robot is awake.
        if animation.current_state != "idle":
            eyl = animation.servos["EYL"]
            eyr = animation.servos["EYR"]
            pit = animation.servos["PIT"]
            yaw = animation.servos["YAW"]

            if offset:
                dead = self.external.deadzone
                static = self.external.staticflag

                x0, y0 = offset
                x_scale = self.external.x_adj_factor / 110
                y_scale = self.external.y_adj_factor / 110

                if not static:
                    if abs(x0) > dead:
                        x = eyl.target + x0 * x_scale
                        eyl.set_target(x)
                        eyr.set_target(x)

                    if abs(y0) > dead:
                        y = pit.target + y0 * y_scale
                        pit.set_target(y)

            if abs(90 - eyl.target) >= 20:
                self.yaw_countdown -= 1
                if self.yaw_countdown <= 0:
                    yaw.set_target(90 + ((eyl.target - 90) / 2))
                    self.yaw_countdown = self.yaw_target
