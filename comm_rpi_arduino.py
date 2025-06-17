#!/usr/bin/python3



import serial

import time



ser = serial.Serial('/dev/ttyACM0', 9600, timeout=5)



# read from Arduino

input_str = ser.readline()

print ("Read input " + input_str.decode("utf-8").strip() + " from Arduino")

while 1:
    ser.write(b'Status\n')
    input_str = ser.readline().decode('utf-8').strip()
    if (input_str == ""):
        print("_")
    else:
        print ("Read input back:" + input_str)

    time.sleep(5)

    ser.write(b'set on\n')
    input_str = ser.readline().decode("utf-8").strip()
    if (input_str == ""): 
        print("_")
    else:
        print ("Read input back:" + input_str)

    time.sleep(5)

    ser.write(b'set off\n')
    input_str = ser.readline().decode("utf-8").strip()
    if (input_str == ""): 
        print("_")
    else:
        print ("Read input back:" + input_str)

    time.sleep(5)