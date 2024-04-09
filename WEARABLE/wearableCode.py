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
from pyb import Pin
import sys
# VL53L1X ToF sensor basic distance measurement example.
from machine import I2C
from vl53l1x import VL53L1X
import socket

from machine import Pin
from machine import SPI
from lsm6dsox import LSM6DSOX
import sensor

import network
import omv
import rtsp
import sensor
import time
import sys
# VL53L1X ToF sensor basic distance measurement example.
from machine import I2C
from vl53l1x import VL53L1X
import socket
import random
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


server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.setsockopt(socket.SOL_SOCKET, 0x20, 1)
# Enable broadcasting mode
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.setsockopt(socket.SOL_SOCKET, 0x20, 1)
server.bind(("", 30000))
last_sent = "None"

change_Mode_prox = False
change_Mode_all = False
change_Mode_participant = False

def generate_random_id(length=6):
    digits = '0123456789'
    return ''.join(random.choice(digits) for _ in range(length))

while True:
    if change_Mode_all == False:
        print("here")
        red_led.on()
        start = pyb.millis()
        if (tof.read() < 50):
            current_time = pyb.millis()
            elapsed = current_time - start
            while (tof.read() < 50):
                elapsed = pyb.elapsed_millis(start)
                print(pyb.elapsed_millis(start))
                if elapsed <= 10000:
                    if elapsed < 500:
                        sendData = "wearablePulse X "+ generate_random_id(6) +" pulse:short rgb:(100,0,100)"
                        print(sendData)
                        red_led.on()
                        blue_led.on()
                        green_led.on()

                    elif (1000 <= elapsed < 1500):
                        sendData = "wearablePulse X "+ generate_random_id(6) +" pulse:medium rgb:(100,0,100)"
                        print(sendData)
                        red_led.on()
                        blue_led.off()
                        green_led.off()
                    elif (2000 <= elapsed < 4000):
                        sendData = "wearablePulse X "+ generate_random_id(6) +" pulse:long rgb:(100,0,100)"
                        print(sendData)
                        red_led.off()
                        blue_led.on()
                        green_led.off()
                    elif (7000 > elapsed >= 6000):
                        change_Mode_all = True
                        sendData = "change to IMU"
                        print(sendData)
                        red_led.off()
                        blue_led.off()
                        green_led.on()
                    elif (elapsed >= 9000):
                        change_Mode_participant = True
                        sendData = "change to participant mode"
                        print(sendData)
                        red_led.on()
                        blue_led.on()
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

    elif change_Mode_participant == True:
        print("here3")
        lsm = LSM6DSOX(SPI(5), cs=Pin("PF6", Pin.OUT_PP, Pin.PULL_UP))

        # Thresholds
        UP_DOWN_THRESHOLD = 0.8  # Threshold to detect up or down orientation
        IMPACT_THRESHOLD = 1.2  # Acceleration threshold to detect an impact

        start = pyb.millis()
        while True:
            green_led.on()
            while (tof.read() < 50):
                current_time = pyb.millis()
                elapsed = current_time - start
                print(elapsed)
                if (11000 > elapsed >= 10000):
                    print(elapsed)
                    change_Mode_all = False
                    change_Mode_prox = False
                    break
                if (elapsed >= 11000):
                    print(elapsed)
                    change_Mode_all = True
                    change_Mode_participant = False
                    break
                break
            if change_Mode_all == False:
                break
            sendData = ""
            # Read accelerometer data
            accel_x, accel_y, accel_z = lsm.accel()

            # Detect orientation for x-axis
            if accel_x > UP_DOWN_THRESHOLD:
                sendData = "wearablePaint X "+ generate_random_id(6) +" direction:x-axis-up rgb:(100,0,50)"
                print(sendData)
                module_picked = random.randint(0, 35)
                server.sendto(sendData.encode(), ('255.255.255.255', 50000 + module_picked))
                server.sendto(sendData.encode(), ('255.255.255.255', 50000 + module_picked))
                server.sendto(sendData.encode(), ('255.255.255.255', 50000 + module_picked))
                time.sleep(1)

            elif accel_x < -UP_DOWN_THRESHOLD:
                sendData = "wearablePaint X "+ generate_random_id(6) +" direction:x-axis-down rgb:(100,100,0)"
                print(sendData)
                module_picked = random.randint(0, 35)
                server.sendto(sendData.encode(), ('255.255.255.255', 50000 + module_picked))
                server.sendto(sendData.encode(), ('255.255.255.255', 50000 + module_picked))
                server.sendto(sendData.encode(), ('255.255.255.255', 50000 + module_picked))
                time.sleep(1)


            # Detect orientation for y-axis
            if accel_y > UP_DOWN_THRESHOLD:
                sendData = "wearablePaint X "+ generate_random_id(6) +" direction:y-axis-up rgb:(0,0,0)"
                print(sendData)
                for i in range(36):
                    server.sendto(sendData.encode(), ('255.255.255.255', 50000 + i))
                    server.sendto(sendData.encode(), ('255.255.255.255', 50000 + i))
                time.sleep(1)

            elif accel_y < -UP_DOWN_THRESHOLD:
                sendData = "wearablePaint X "+ generate_random_id(6) +" direction:y-axis-down rgb:(50,100,0)"
                print(sendData)
                for i in range(36):
                    server.sendto(sendData.encode(), ('255.255.255.255', 50000 + i))
                    server.sendto(sendData.encode(), ('255.255.255.255', 50000 + i))
                time.sleep(1)


            # Detect orientation for z-axis
            if accel_z > UP_DOWN_THRESHOLD:
                sendData = "wearablePaint X "+ generate_random_id(6) +" direction:z-axis-up rgb:(100,50,50)"
                print(sendData)
                module_picked = random.randint(0, 35)
                server.sendto(sendData.encode(), ('255.255.255.255', 50000 + module_picked))
                server.sendto(sendData.encode(), ('255.255.255.255', 50000 + module_picked))
                server.sendto(sendData.encode(), ('255.255.255.255', 50000 + module_picked))
                time.sleep(1)

            elif accel_z < -UP_DOWN_THRESHOLD:
                sendData = "wearablePaint X "+ generate_random_id(6) +" direction:z-axis-down rgb:(0,50,100)"
                print(sendData)
                module_picked = random.randint(0, 35)
                server.sendto(sendData.encode(), ('255.255.255.255', 50000 + module_picked))
                server.sendto(sendData.encode(), ('255.255.255.255', 50000 + module_picked))
                server.sendto(sendData.encode(), ('255.255.255.255', 50000 + module_picked))
                time.sleep(1)


    elif change_Mode_all == True:
        print("here2")
        lsm = LSM6DSOX(SPI(5), cs=Pin("PF6", Pin.OUT_PP, Pin.PULL_UP))

        # Thresholds
        UP_DOWN_THRESHOLD = 0.8  # Threshold to detect up or down orientation
        IMPACT_THRESHOLD = 1.2  # Acceleration threshold to detect an impact

        start = pyb.millis()
        while True:
            green_led.on()
            while (tof.read() < 50):
                current_time = pyb.millis()
                elapsed = current_time - start
                print(elapsed)
                if (11000 > elapsed >= 10000):
                    print(elapsed)
                    change_Mode_all = False
                    change_Mode_prox = False
                    break
                if (elapsed >= 12000):
                    print(elapsed)
                    change_Mode_all = False
                    change_Mode_participant = True
                    break
                break
            if change_Mode_all == False:
                break
            sendData = ""
            # Read accelerometer data
            accel_x, accel_y, accel_z = lsm.accel()

            # Detect orientation for x-axis
            if accel_x > UP_DOWN_THRESHOLD:
                sendData = "wearableIMU X "+ generate_random_id(6) +" direction:x-axis-up rgb:(100,0,50)"
                print("X-axis is up.")
                module_picked = random.randint(0, 35)
                server.sendto(sendData.encode(), ('255.255.255.255', 50000 + module_picked))
                server.sendto(sendData.encode(), ('255.255.255.255', 50000 + module_picked))
                server.sendto(sendData.encode(), ('255.255.255.255', 50000 + module_picked))
                time.sleep(1)

            elif accel_x < -UP_DOWN_THRESHOLD:
                sendData = "wearableIMU X "+ generate_random_id(6) +" direction:x-axis-down rgb:(100,100,0)"
                print("X-axis is down.")
                module_picked = random.randint(0, 35)
                server.sendto(sendData.encode(), ('255.255.255.255', 50000 + module_picked))
                server.sendto(sendData.encode(), ('255.255.255.255', 50000 + module_picked))
                server.sendto(sendData.encode(), ('255.255.255.255', 50000 + module_picked))
                time.sleep(1)


            # Detect orientation for y-axis
            if accel_y > UP_DOWN_THRESHOLD:
                sendData = "wearableIMU X "+ generate_random_id(6) +" direction:y-axis-up rgb:(0,0,0)"
                print("Y-axis is up.")
                for i in range(36):
                    server.sendto(sendData.encode(), ('255.255.255.255', 50000 + i))
                    server.sendto(sendData.encode(), ('255.255.255.255', 50000 + i))
                    server.sendto(sendData.encode(), ('255.255.255.255', 50000 + i))
                time.sleep(1)

            elif accel_y < -UP_DOWN_THRESHOLD:
                sendData = "wearableIMU X "+ generate_random_id(6) +" direction:y-axis-down rgb:(50,100,0)"
                print("Y-axis is down.")
                for i in range(36):
                    server.sendto(sendData.encode(), ('255.255.255.255', 50000 + i))
                    server.sendto(sendData.encode(), ('255.255.255.255', 50000 + i))
                    server.sendto(sendData.encode(), ('255.255.255.255', 50000 + i))
                time.sleep(1)


            # Detect orientation for z-axis
            if accel_z > UP_DOWN_THRESHOLD:
                sendData = "wearableIMU X "+ generate_random_id(6) +" direction:z-axis-up rgb:(100,50,50)"
                print("Z-axis is up.")
                module_picked = random.randint(0, 35)
                server.sendto(sendData.encode(), ('255.255.255.255', 50000 + module_picked))
                server.sendto(sendData.encode(), ('255.255.255.255', 50000 + module_picked))
                server.sendto(sendData.encode(), ('255.255.255.255', 50000 + module_picked))
                time.sleep(1)

            elif accel_z < -UP_DOWN_THRESHOLD:
                sendData = "wearableIMU X "+ generate_random_id(6) +" direction:z-axis-down rgb:(0,50,100)"
                print("Z-axis is down.")
                module_picked = random.randint(0, 35)
                server.sendto(sendData.encode(), ('255.255.255.255', 50000 + module_picked))
                server.sendto(sendData.encode(), ('255.255.255.255', 50000 + module_picked))
                server.sendto(sendData.encode(), ('255.255.255.255', 50000 + module_picked))
                time.sleep(1)
