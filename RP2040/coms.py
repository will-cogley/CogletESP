from machine import Pin, UART
import time
import animation # Assuming this handles your state_map

class Comms:
    def __init__(self):
        # Hardware Initialization
        self.grove = UART(0, baudrate=921600, tx=Pin(0), rx=Pin(1))
        self.esp = UART(1, baudrate=115200, tx=Pin(4), rx=Pin(5))
        
        # Constants
        self.INVOKE_CMD = b"AT+INVOKE=1,0,1\r"
        self.pixel_centre = 112
        self.deadzone = 20
        self.x_adj_factor = 10
        self.y_adj_factor = 10
        self.staticflag = False
        
        # Buffers and State
        self.cbuf = b""
        self.rx_buffer = b""
        self.readflag = True
        self.last_boxes = None

    def map_value(self, value, in_min, in_max, out_min, out_max):
        return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    def esp_read(self):
        if self.esp.any():
            # Read all available bytes in one operation
            self.rx_buffer += self.esp.read()
            
            # Process complete lines
            while b"\n" in self.rx_buffer:
                line, self.rx_buffer = self.rx_buffer.split(b"\n", 1)
                rcvstate = line.decode('utf-8').strip()
                
                if rcvstate in animation.state_map:
                    return rcvstate
        return None

    def grove_read(self):
        # State 1: Requesting data
        if self.readflag:
            # Flush existing buffer quickly
            while self.grove.any():
                self.grove.read()
                
            self.grove.write(self.INVOKE_CMD)
            self.cbuf = b""
            self.readflag = False
            return None # Return early, data isn't ready yet

        # State 2: Receiving data
        if self.grove.any():
            # PERFORMANCE: Read chunks directly instead of looping char by char
            self.cbuf += self.grove.read()
            
            # Wait until the end of the JSON packet arrives
            if b'"resolution"' in self.cbuf:
                key = b'"boxes":'
                i = self.cbuf.find(key)
                
                if i != -1:
                    boxes_part = self.cbuf[i + len(key):]
                    
                    # Ensure we have the closing bracket before slicing
                    end_idx = boxes_part.find(b']')
                    if end_idx != -1:
                        boxes_part = boxes_part[:end_idx + 1].strip()
                        
                        # Process if we have valid, new box data
                        if boxes_part != b'[]' and boxes_part != self.last_boxes:
                            self.staticflag = False
                            self.last_boxes = boxes_part
                            boxes_str = boxes_part.decode('utf-8').strip('[]')
                            
                            try:
                                numbers = [int(n) for n in boxes_str.split(',')]
                                x_offset = numbers[0] - self.pixel_centre
                                y_offset = numbers[1] - self.pixel_centre
                                
                                # Reset for next read
                                self.cbuf = b""
                                self.readflag = True
                                return x_offset, y_offset
                                
                            except ValueError:
                                # Handle cases where split data isn't a perfect integer
                                pass
                        else:
                            # Reset for next read (static or empty data)
                            self.cbuf = b""
                            self.readflag = True
                            self.staticflag = True
                            return None
                            
        return None

