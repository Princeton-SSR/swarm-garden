# This work is licensed under the MIT license.
# Copyright (c) 2013-2023 OpenMV LLC. All rights reserved.
# https://github.com/openmv/openmv/blob/master/LICENSE
#
# Hello World Example
#
# Welcome to the OpenMV IDE! Click on the green run arrow button below to run the script!

#import sensor
import time
import pyb
from pyb import LED
import random
import network
import omv
import rtsp
#import sensor
import time
from pyb import Pin
import time
import sys
# VL53L1X ToF sensor basic distance measurement example.
from machine import I2C
from vl53l1x import VL53L1X
import time
import socket

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

tof = VL53L1X(I2C(2))


INT_MODE = True  # Run in interrupt mode.
INT_FLAG = False  # Set True on interrupt.

red_led = LED(1)
green_led = LED(2)
blue_led = LED(3)


network_if = network.WLAN(network.STA_IF)
network_if.active(True)
network_if.connect("SwarmGarden", "swarmgardenhorray123!")
while not network_if.isconnected():
    print("Trying to connect. Note this may take a while...")
    blue_led.on()
    time.sleep_ms(1000)

blue_led.off()

#while True:
#    red_led.on()
#, socket.IPPROTO_UDP
#socket.SO_REUSEPORT
#, socket.IPPROTO_UDP
#socket.SO_REUSEPORT,
#socket.SO_BROADCAST,

#SOF_BROADCAST = const(0x20)

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.setsockopt(socket.SOL_SOCKET, 0x20, 1)
# Enable broadcasting mode
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.setsockopt(socket.SOL_SOCKET, 0x20, 1)
server.bind(("", 30000))
last_sent = "None"

change_Mode_prox = False
change_Mode_all = False


while True:
    if change_Mode_all == False and change_Mode_prox == False:
        print("here")
        red_led.on()
        start = pyb.millis()
        if (tof.read() < 50):
            current_time = pyb.millis()
            elapsed = current_time - start
            while (tof.read() < 50):
                elapsed = pyb.elapsed_millis(start)
                print(pyb.elapsed_millis(start))
                if elapsed <= 8000:
                    if elapsed < 500:
                        sendData = "wearablePulse X pulse:short rgb:(100,0,100)"
                        print(sendData)
                        red_led.on()
                        blue_led.on()
                        green_led.on()

                    elif (1000 <= elapsed < 1500):
                        sendData = "wearablePulse X pulse:medium rgb:(100,0,100)"
                        print(sendData)
                        red_led.on()
                        blue_led.off()
                        green_led.off()
                    elif (2000 <= elapsed < 4000):
                        sendData = "wearablePulse X pulse:long rgb:(100,0,100)"
                        print(sendData)
                        red_led.off()
                        blue_led.on()
                        green_led.off()
                    elif (7000 > elapsed >= 6000):
                        change_Mode_prox = True
                        sendData = "change prox mode"
                        print(sendData)
                        red_led.off()
                        blue_led.on()
                        green_led.on()
                    elif (elapsed >= 7000):
                        change_Mode_all = True
                        sendData = "change to IMU"
                        print(sendData)
                        red_led.off()
                        blue_led.off()
                        green_led.on()
                else:
                    break
                pyb.delay(100)
        else:
            red_led.off()
            green_led.off()
            blue_led.off()
            continue
        for i in range(36):
            server.sendto(sendData.encode(), ('255.255.255.255', 50000 + i))

    elif change_Mode_all == False and change_Mode_prox == True:

        print("here1")
        blue_led.on()
        start = pyb.millis()
        if (tof.read() < 50):
            current_time = pyb.millis()
            elapsed = current_time - start
            while (tof.read() < 50):
                elapsed = pyb.elapsed_millis(start)
                print(pyb.elapsed_millis(start))
                if elapsed <= 8000:
                    if elapsed < 500:
                        sendData = "wearableExpand X expand:short rgb:(100,0,100)"
                        print(sendData)
                        red_led.on()
                        blue_led.on()
                        green_led.on()
                    elif (1000 <= elapsed < 1500):
                        sendData = "wearableExpand X expand:medium rgb:(50,0,100)"
                        print(sendData)
                        red_led.on()
                        blue_led.off()
                        green_led.off()
                    elif (2000 <= elapsed < 4000):
                        sendData = "wearableExpand X expand:long rgb:(0,0,100)"
                        print(sendData)
                        red_led.off()
                        blue_led.on()
                        green_led.off()
                    elif (7000 > elapsed >= 6000):
                        change_Mode_prox = False
                        sendData = "change prox mode"
                        print(sendData)
                        red_led.off()
                        blue_led.off()
                        green_led.on()
                    elif (elapsed >= 7000):
                        change_Mode_all = True
                        sendData = "change to IMU"
                        print(sendData)
                        red_led.off()
                        blue_led.off()
                        green_led.on()
                else:
                    break
                pyb.delay(100)
        else:
            red_led.off()
            green_led.off()
            blue_led.off()
            continue

        module_picked = random.randint(0, 35)
        server.sendto(sendData.encode(), ('255.255.255.255', 50000 + module_picked))

    elif change_Mode_all == True:
        print("here2")
        lsm = LSM6DSOX(SPI(5), cs=Pin("PF6", Pin.OUT_PP, Pin.PULL_UP))

        # Thresholds
        UP_DOWN_THRESHOLD = 0.8  # Threshold to detect up or down orientation
        IMPACT_THRESHOLD = 1.5  # Acceleration threshold to detect an impact

        def calculate_magnitude(x, y, z):
            """Calculate the magnitude of the acceleration vector."""
            return math.sqrt(x**2 + y**2 + z**2)

        start = pyb.millis()
        while True:
            green_led.on()
            while (tof.read() < 50):
                current_time = pyb.millis()
                elapsed = current_time - start
                print(elapsed)
                if (elapsed >= 7000):
                    print(elapsed)
                    change_Mode_all = False
                    change_Mode_prox = False
                    break
                break
            if change_Mode_all == False:
                break
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



