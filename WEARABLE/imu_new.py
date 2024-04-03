## This work is licensed under the MIT license.
## Copyright (c) 2013-2023 OpenMV LLC. All rights reserved.
## https://github.com/openmv/openmv/blob/master/LICENSE
##
## Hello World Example
##
## Welcome to the OpenMV IDE! Click on the green run arrow button below to run the script!


from machine import Pin
from machine import SPI
from lsm6dsox import LSM6DSOX
import sensor
import time
import pyb
from pyb import LED

import network
import omv
import rtsp
import sensor
import time
from pyb import Pin
import time
import sys
# VL53L1X ToF sensor basic distance measurement example.
from machine import I2C
from vl53l1x import VL53L1X
import time
import socket
import socket
import time
import math


#INT_MODE = True  # Run in interrupt mode.
#INT_FLAG = False  # Set True on interrupt.

#redLED = pyb.LED(1) # built-in red LED
#greenLED = pyb.LED(2) # built-in green LED
#blueLED = pyb.LED(3) # built-in blue LED

#network_if = network.WLAN(network.STA_IF)
#network_if.active(True)
#network_if.connect("SwarmGarden", "swarmgardenhorray123!")
#while not network_if.isconnected():
#    print("Trying to connect. Note this may take a while...")
#    blueLED.on()
#    time.sleep_ms(1000)

#print("connected")
#blueLED.off()

#while True:
#    red_led.on()
#, socket.IPPROTO_UDP
#socket.SO_REUSEPORT
#, socket.IPPROTO_UDP
#socket.SO_REUSEPORT,
#socket.SO_BROADCAST,

#SOF_BROADCAST = const(0x20)

#server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#server.setsockopt(socket.SOL_SOCKET, 0x20, 1)
## Enable broadcasting mode
#server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#server.setsockopt(socket.SOL_SOCKET, 0x20, 1)
#server.bind(("", 30000))

#import sensor
#import time

#sensor.reset()  # Reset and initialize the sensor.
#sensor.set_pixformat(sensor.RGB565)  # Set pixel format to RGB565 (or GRAYSCALE)
#sensor.set_framesize(sensor.QVGA)  # Set frame size to QVGA (320x240)
#sensor.skip_frames(time=2000)  # Wait for settings take effect.
#clock = time.clock()  # Create a clock object to track the FPS.

#while True:
#    clock.tick()  # Update the FPS clock.
#    img = sensor.snapshot()  # Take a picture and return the image.
#    print(clock.fps())  # Note: OpenMV Cam runs about half as fast when connected
#    # to the IDE. The FPS should increase once disconnected.

#import time
#from lsm6dsox import LSM6DSOX
#from machine import Pin, SPI

## Initialize the sensor
#lsm = LSM6DSOX(SPI(5), cs=Pin("PF6", Pin.OUT_PP, Pin.PULL_UP))

## Thresholds and parameters
#GYRO_THRESHOLD = 0.1  # Detection threshold for gyroscope
#RIGHT_MOVEMENT_DETECTED = False  # State to track if right movement was detected

#while True:
#    # Read accelerometer and gyroscope data
#    accel_x, accel_y, accel_z = lsm.accel()
#    _, gyro_y, _ = lsm.gyro()  # Gyroscope y-axis for detecting rotation around x-axis

#    # Print the gyroscope data for debugging
#    print(gyro_y)

#    # Gyroscope-based orientation detection for x-axis movement
#    if gyro_y > GYRO_THRESHOLD:
#        print("X-axis is rotating to the right.")
#        RIGHT_MOVEMENT_DETECTED = True
#    elif gyro_y < -GYRO_THRESHOLD and not RIGHT_MOVEMENT_DETECTED:
#        print("X-axis is rotating to the left.")
#    elif RIGHT_MOVEMENT_DETECTED and abs(gyro_y) <= GYRO_THRESHOLD * 0.9:
#        # This condition checks if we're returning to a lesser tilt from the right
#        print("Returning to center, maintain right orientation state.")
#    else:
#        # Reset right movement detection if the gyroscope's y-axis reading stabilizes
#        RIGHT_MOVEMENT_DETECTED = False

#    time.sleep_ms(100)

#import time
#from lsm6dsox import LSM6DSOX
#from machine import Pin, SPI
#import math

## Initialize the sensor
#lsm = LSM6DSOX(SPI(5), cs=Pin("PF6", Pin.OUT_PP, Pin.PULL_UP))

## Thresholds and parameters
#GYRO_THRESHOLD = 0.9
#UP_DOWN_THRESHOLD = 0.8
#IMPACT_THRESHOLD = 1.5
#MOVEMENT_DETECTED = False  # State to track movement direction

#def calculate_magnitude(x, y, z):
#    """Calculate the magnitude of the acceleration vector."""
#    return math.sqrt(x**2 + y**2 + z**2)

#while True:
#    # Read accelerometer and gyroscope data
#    accel_x, accel_y, accel_z = lsm.accel()
#    _, gyro_y, _ = lsm.gyro()

#    # Orientation detection for x-axis and z-axis
#    if accel_x > UP_DOWN_THRESHOLD:
#        print("X-axis is up.")
#    elif accel_x < -UP_DOWN_THRESHOLD:
#        print("X-axis is down.")

#    if accel_z > UP_DOWN_THRESHOLD:
#        print("Z-axis is up.")
#    elif accel_z < -UP_DOWN_THRESHOLD:
#        print("Z-axis is down.")

#    # Impact detection
#    accel_magnitude = calculate_magnitude(accel_x, accel_y, accel_z) - 1
#    if accel_magnitude > IMPACT_THRESHOLD:
#        print("Impact detected!")

#    # Y-axis orientation and gyro-based movement detection
#    if accel_y < -UP_DOWN_THRESHOLD:  # Check if the y-axis is down
#        print("Y-axis is down.")
#        if gyro_y > GYRO_THRESHOLD:
#            print("X-axis is rotating to the right.")
#            MOVEMENT_DETECTED = 'right'
#        elif gyro_y < -GYRO_THRESHOLD:
#            print("X-axis is rotating to the left.")
#            MOVEMENT_DETECTED = 'left'
#        elif MOVEMENT_DETECTED == 'right' and abs(gyro_y) <= GYRO_THRESHOLD * 0.9:
#            print("Returning to center from right.")
#        elif MOVEMENT_DETECTED == 'left' and abs(gyro_y) >= -GYRO_THRESHOLD * 0.9:
#            print("Returning to center from left.")
#        else:
#            MOVEMENT_DETECTED = False
#    else:
#        print("Y-axis is not down.")
#        MOVEMENT_DETECTED = False

#    time.sleep_ms(100)

#import time
#from lsm6dsox import LSM6DSOX
#from machine import Pin, SPI
#import math

## Initialize the sensor
#lsm = LSM6DSOX(SPI(5), cs=Pin("PF6", Pin.OUT_PP, Pin.PULL_UP))

## Thresholds and parameters
#GYRO_THRESHOLD = 0.5
#UP_DOWN_THRESHOLD = 0.8
#IMPACT_THRESHOLD = 1.5
#movement_state = None  # Tracks the current significant movement direction

#def calculate_magnitude(x, y, z):
#    """Calculate the magnitude of the acceleration vector."""
#    return math.sqrt(x**2 + y**2 + z**2)

#while True:
#    # Read accelerometer and gyroscope data
#    accel_x, accel_y, accel_z = lsm.accel()
#    _, gyro_y, _ = lsm.gyro()

#    # Orientation detection for x-axis and z-axis
#    if accel_x > UP_DOWN_THRESHOLD:
#        print("X-axis is up.")
#    elif accel_x < -UP_DOWN_THRESHOLD:
#        print("X-axis is down.")

#    if accel_z > UP_DOWN_THRESHOLD:
#        print("Z-axis is up.")
#    elif accel_z < -UP_DOWN_THRESHOLD:
#        print("Z-axis is down.")

#    # Impact detection
#    accel_magnitude = calculate_magnitude(accel_x, accel_y, accel_z) - 1
#    if accel_magnitude > IMPACT_THRESHOLD:
#        print("Impact detected!")

#    # Y-axis orientation and gyro-based movement detection
#    if accel_y < -UP_DOWN_THRESHOLD:  # Y-axis down
#        print("Y-axis is down.")
#        if gyro_y > GYRO_THRESHOLD:
#            if movement_state != 'left':  # Avoid flipping direction unless clear change
#                movement_state = 'right'
#                print("X-axis is rotating to the right.")
#        elif gyro_y < -GYRO_THRESHOLD:
#            if movement_state != 'right':  # Avoid flipping direction unless clear change
#                movement_state = 'left'
#                print("X-axis is rotating to the left.")
#        # No else branch; we don't update the state when slowing down
#    else:
#        movement_state = None  # Reset when Y-axis is not down

#    time.sleep_ms(100)


#import time
#from lsm6dsox import LSM6DSOX
#from machine import Pin, SPI
#import math

## Initialize the sensor
#lsm = LSM6DSOX(SPI(5), cs=Pin("PF6", Pin.OUT_PP, Pin.PULL_UP))

## Thresholds and parameters
#GYRO_THRESHOLD = 0.1  # Gyroscope threshold for detecting rotation
#UP_DOWN_THRESHOLD = 0.8  # Threshold for detecting if an axis is up or down
#IMPACT_THRESHOLD = 1.5  # Threshold for detecting impact

## Function to calculate the magnitude of the acceleration vector
#def calculate_magnitude(x, y, z):
#    """Calculate the magnitude of the acceleration vector."""
#    return math.sqrt(x**2 + y**2 + z**2)

## Initial state for movement to ensure it's not changed by minor fluctuations
#movement_state = None

#while True:
#    # Read accelerometer and gyroscope data
#    accel_x, accel_y, accel_z = lsm.accel()
#    _, gyro_y, _ = lsm.gyro()

#    # Orientation detection for x-axis and z-axis
#    if accel_x > UP_DOWN_THRESHOLD:
#        print("X-axis is up.")
#    elif accel_x < -UP_DOWN_THRESHOLD:
#        print("X-axis is down.")

#    if accel_z > UP_DOWN_THRESHOLD:
#        print("Z-axis is up.")
#    elif accel_z < -UP_DOWN_THRESHOLD:
#        print("Z-axis is down.")

#    # Impact detection based on acceleration magnitude
#    accel_magnitude = calculate_magnitude(accel_x, accel_y, accel_z) - 1
#    if accel_magnitude > IMPACT_THRESHOLD:
#        print("Impact detected!")

#    # Movement direction detection based on gyro_y
#    if accel_y < -UP_DOWN_THRESHOLD:  # Check if y-axis is down
#        # Determine directional movement only when y-axis is down
#        if gyro_y > GYRO_THRESHOLD and movement_state != 'right':
#            print("X-axis is rotating to the right.")
#            movement_state = 'right'
#        elif gyro_y < -GYRO_THRESHOLD and movement_state != 'left':
#            print("X-axis is rotating to the left.")
#            movement_state = 'left'
#    else:
#        # Reset movement state when not in the specific y-axis down orientation
#        movement_state = None

#    time.sleep_ms(100)

# Initialize the sensor
lsm = LSM6DSOX(SPI(5), cs=Pin("PF6", Pin.OUT_PP, Pin.PULL_UP))

# Thresholds
UP_DOWN_THRESHOLD = 0.8  # Threshold to detect up or down orientation
IMPACT_THRESHOLD = 1.5  # Acceleration threshold to detect an impact

def calculate_magnitude(x, y, z):
    """Calculate the magnitude of the acceleration vector."""
    return math.sqrt(x**2 + y**2 + z**2)

while True:
    sendData = ""
    # Read accelerometer data
    accel_x, accel_y, accel_z = lsm.accel()

    # Detect orientation for x-axis
    if accel_x > UP_DOWN_THRESHOLD:
        sendData = "wearableIMU X direction:x-axis-up rgb:(100,0,50)"
        print("X-axis is up.")
    elif accel_x < -UP_DOWN_THRESHOLD:
        sendData = "wearableIMU X direction:x-axis-down rgb:(100,100,0)"
        print("X-axis is down.")

    # Detect orientation for y-axis
    if accel_y > UP_DOWN_THRESHOLD:
        sendData = "wearableIMU X direction:y-axis-up rgb:(100,50,0)"
        print("Y-axis is up.")
    elif accel_y < -UP_DOWN_THRESHOLD:
        sendData = "wearableIMU X direction:y-axis-down rgb:(50,100,0)"
        print("Y-axis is down.")

    # Detect orientation for z-axis
    if accel_z > UP_DOWN_THRESHOLD:
        sendData = "wearableIMU X direction:z-axis-up rgb:(100,50,50)"
        print("Z-axis is up.")
    elif accel_z < -UP_DOWN_THRESHOLD:
        sendData = "wearableIMU X direction:z-axis-down rgb:(0,50,100)"
        print("Z-axis is down.")

    # Detect impact based on acceleration magnitude
    accel_magnitude = calculate_magnitude(accel_x, accel_y, accel_z) - 1  # Subtract 1g for the stationary effect
    if accel_magnitude > IMPACT_THRESHOLD:
        sendData = "wearableIMU X direction:impact rgb:(100,0,0)"
        print("Impact detected!")

    time.sleep_ms(100)


    server.sendto(sendData.encode(), ('255.255.255.255', 50000))
    server.sendto(sendData.encode(), ('255.255.255.255', 50000))
#    server.sendto(sendData.encode(), ('255.255.255.255', 50000))
#    server.sendto(sendData.encode(), ('255.255.255.255', 50000))
