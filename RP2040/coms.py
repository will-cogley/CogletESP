import time
from machine import Pin, I2C, ADC, UART
import time, random, ujson, urandom, sys, select, uselect, math
import animation

INVOKE_CMD = b"AT+INVOKE=1,0,1\r"
cbuf = []
readflag = True
staticflag = False
last_boxes = None
detected_flag = False
static_target = 200
static_timer = static_target
idle_flag = False
idle_pause = 300

deadzone = 20
x_offset = 0
y_offset = 0
x_adj_factor = 10
y_adj_factor = 10
pixel_centre = 112
tl_target = 90
tr_target = 90
bl_target = 90
br_target = 90

grove = UART(0, baudrate=921600, tx=Pin(0), rx=Pin(1))
ESP = UART(1, baudrate=115200, tx=Pin(4), rx=Pin(5))
rx_buffer = b""

def map_value(value, in_min, in_max, out_min, out_max):
    # Map the value
    mapped = (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
    return mapped

def ESP_read():
    global rx_buffer
    if ESP.any():
        rx_buffer += ESP.read()   # bytes + bytes = OK
        while b"\n" in rx_buffer:
            line, rx_buffer = rx_buffer.split(b"\n", 1)
            rcvstate = line.decode().strip()
#             print("RX:", rcvstate)
            if rcvstate in animation.state_map:
                return rcvstate
                

def grove_read():
    global cbuf, readflag, staticflag, last_boxes, x_offset, y_offset
    if readflag == True:
        while grove.any():
            grove.read()
        grove.write(INVOKE_CMD)
        cbuf = b""
        readflag = False
    if readflag == False:
        if grove.any():
            data = grove.read()
            for ch in data:
                cbuf += bytes([ch]) 
            if b'"resolution"' in cbuf:
                key = b'"boxes":'
                i = cbuf.find(key)
                if i != -1:
                    boxes_part = cbuf[i + len(key):]
                    boxes_part = boxes_part[:boxes_part.find(b']') + 1]
                    boxes_part = boxes_part.strip()
                    if boxes_part != b'[]' and boxes_part != last_boxes:
                        staticflag = False
                        boxes_str = boxes_part.decode('utf-8').strip('[]')
                        numbers = [int(n) for n in boxes_str.split(',')]
                        x_offset, y_offset = numbers[0] - pixel_centre, numbers[1] - pixel_centre
#                         print("x: ", x_offset, "y: ", y_offset)
                        last_boxes = boxes_part
                    else:
                        x_offset, y_offset = 0, 0
                        staticflag = True
                    
                cbuf = b""
                readflag = True
                if staticflag == False:
                    return x_offset, y_offset
                else:
                    return None
#             time.sleep_ms(5)
