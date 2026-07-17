from machine import Pin, UART
import time
import ujson


class Comms:
    def __init__(self):
        # Grove Vision AI V2
        self.grove = UART(
            0,
            baudrate=921600,
            tx=Pin(0),
            rx=Pin(1),
        )

        # ESP32 <-> RP2040 internal UART
        self.esp = UART(
            1,
            baudrate=115200,
            tx=Pin(4),
            rx=Pin(5),
        )

        # SSCMA continuous inference:
        # -1 = run continuously
        #  0 = emit every result, not only changed results
        #  1 = result only; do not include image data
        self.INVOKE_CMD = b"AT+INVOKE=-1,0,1\r"
        self.BREAK_CMD = b"AT+BREAK\r"

        # Preserve Will's original tracking parameters.
        self.pixel_centre = 112
        self.deadzone = 20
        self.x_adj_factor = 10
        self.y_adj_factor = 10
        self.staticflag = False

        # Independent UART receive buffers.
        self.cbuf = b""
        self.rx_buffer = b""

        # Face-result state.
        self.last_boxes = None
        self.stream_started = False
        self.last_event_ms = time.ticks_ms()

        # Diagnostics; these do not change tracking behavior.
        self.frame_count = 0
        self.empty_count = 0
        self.dropped_frames = 0
        self.protocol_errors = 0

        self.start_grove_stream()

    def _drain_grove_uart(self):
        while self.grove.any():
            self.grove.read()

    def start_grove_stream(self):
        """Stop any old task, clear late bytes, then start one continuous task.

        This is important after a RP2040 soft reset: the Grove module has its
        own processor and may still be running the previous continuous invoke.
        """
        self.grove.write(self.BREAK_CMD)
        time.sleep_ms(80)

        self._drain_grove_uart()
        self.cbuf = b""

        self.grove.write(self.INVOKE_CMD)
        self.stream_started = True
        self.last_event_ms = time.ticks_ms()

        print("Grove continuous mode: AT+INVOKE=-1,0,1")

    def stop_grove_stream(self):
        self.grove.write(self.BREAK_CMD)
        self.stream_started = False

    def map_value(
        self,
        value,
        in_min,
        in_max,
        out_min,
        out_max,
    ):
        return (
            (value - in_min)
            * (out_max - out_min)
            / (in_max - in_min)
            + out_min
        )

    def esp_read(self):
        if self.esp.any():
            chunk = self.esp.read()
            if chunk:
                self.rx_buffer += chunk

        # Avoid unbounded growth if the sender never supplies a newline.
        if len(self.rx_buffer) > 512:
            self.rx_buffer = b""

        commands = []
        while b"\n" in self.rx_buffer:
            line, self.rx_buffer = self.rx_buffer.split(b"\n", 1)
            state = line.decode("utf-8", "ignore").strip()
            if state:
                commands.append(state)

        return commands

    def _parse_reply_line(self, line):
        """Parse one official SSCMA reply unit: CR + JSON + LF."""
        line = line.strip()
        if not line:
            return None

        # Ignore any boot log text surrounding a JSON reply.
        json_start = line.find(b"{")
        json_end = line.rfind(b"}")
        if json_start == -1 or json_end < json_start:
            return None

        try:
            return ujson.loads(
                line[json_start:json_end + 1].decode(
                    "utf-8",
                    "ignore",
                )
            )
        except (ValueError, TypeError):
            self.protocol_errors += 1
            return None

    def grove_read(self):
        """Return only the newest complete face result currently available.

        Continuous mode may deliver several inference events between two
        iterations of main.py. Every complete event is consumed, but only the
        newest event controls the servos. Older queued frames are deliberately
        dropped instead of being replayed one by one.
        """
        if self.grove.any():
            chunk = self.grove.read()
            if chunk:
                self.cbuf += chunk

        # A result-only reply is small. If framing is corrupted, discard the
        # oversized partial buffer rather than retaining stale data forever.
        if len(self.cbuf) > 8192:
            self.cbuf = b""
            self.protocol_errors += 1
            return None

        latest_boxes = None
        invoke_event_count = 0

        # SSCMA defines each reply as CR + JSON + LF, so newline is the packet
        # boundary. Keep the final incomplete fragment for the next call.
        while b"\n" in self.cbuf:
            raw_line, self.cbuf = self.cbuf.split(b"\n", 1)
            message = self._parse_reply_line(raw_line)
            if not message:
                continue

            if (
                message.get("name") == "INVOKE"
                and message.get("code") == 0
            ):
                response_type = message.get("type")

                # type=0 is the command acknowledgement.
                if response_type == 0:
                    self.stream_started = True
                    continue

                # type=1 is one completed inference event.
                if response_type == 1:
                    data = message.get("data")
                    if not isinstance(data, dict):
                        continue

                    boxes = data.get("boxes")
                    if boxes is None:
                        continue

                    latest_boxes = boxes
                    invoke_event_count += 1
                    self.last_event_ms = time.ticks_ms()

        if invoke_event_count == 0:
            return None

        if invoke_event_count > 1:
            self.dropped_frames += invoke_event_count - 1

        self.frame_count += 1

        # Explicit current-frame "no face".
        if not latest_boxes:
            self.empty_count += 1
            self.staticflag = True
            self.last_boxes = ()
            return None

        # Preserve Will's original choice: track the first detection.
        first_box = latest_boxes[0]
        if not isinstance(first_box, (list, tuple)):
            self.protocol_errors += 1
            return None

        if len(first_box) < 2:
            self.protocol_errors += 1
            return None

        # Preserve Will's original coordinate interpretation and duplicate
        # suppression so the existing facetrack.py behavior is unchanged.
        try:
            box_signature = tuple(first_box)
            x_offset = int(first_box[0]) - self.pixel_centre
            y_offset = int(first_box[1]) - self.pixel_centre
        except (ValueError, TypeError):
            self.protocol_errors += 1
            return None

        if box_signature == self.last_boxes:
            self.staticflag = True
            return None

        self.last_boxes = box_signature
        self.staticflag = False
        return x_offset, y_offset
