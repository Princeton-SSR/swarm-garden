# This work is licensed under the MIT license.
# Copyright (c) 2013-2023 OpenMV LLC. All rights reserved.
# https://github.com/openmv/openmv/blob/master/LICENSE
#
# LED Control Example
#
# This example shows how to control the RGB LED.

import sensor
import time
from pyb import LED

from pyb import Pin
from socket import *
import network, time
import time
import sys
# VL53L1X ToF sensor basic distance measurement example.
from machine import I2C
from vl53l1x import VL53L1X
import time
from machine import Pin
import pyb
import select
import neopixel

# This is the only LED pin available on the Nano RP2040,
# other than the RGB LED connected to Nina WiFi module.
#ledBlue = pyb.LED(3)
#ledBlue.on()
SSID='SwarmGarden' # Network SSID
KEY='swarmgardenhorray123!'  # Network key
redLED = pyb.LED(1) # built-in red LED
greenLED = pyb.LED(2) # built-in green LED
blueLED = pyb.LED(3) # built-in blue LED
data = ""

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, KEY)
while not wlan.isconnected():
    print("Trying to connect. Note this may take a while...")
    blueLED.on()
    time.sleep_ms(1000)

print("connected")
blueLED.off()

#while True:
#    red_led.on()
#, socket.IPPROTO_UDP
#socket.SO_REUSEPORT
#, socket.IPPROTO_UDP
#socket.SO_REUSEPORT,
#socket.SO_BROADCAST,

#SOF_BROADCAST = const(0x20)

#server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#server.setsockopt(socket.SOL_SOCKET, 15, 1)
## Enable broadcasting mode
#server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#server.setsockopt(socket.SOL_SOCKET, SOF_BROADCAST, 1)

#wlan.ifconfig(('192.168.0.5', '255.255.255.0', '192.168.0.1', '192.168.0.1'))

# Create socket that can broadcast
s = socket(AF_INET, SOCK_DGRAM)
s.setsockopt(SOL_SOCKET, 0x20, 1)
poller = select.poll()
poller.register(s, select.POLLIN)
# Bind to '' meaning we will listen for any message from any IP
# Bind to port 50000 so we can get messages sent to that port
s.bind(('', 40000))
# careful lowering this, at some point you run into the mechanical limitation of how quick your motor can move
#step_sleep = 0.004
#current_motion = "stop"
#step_count = 100

#step_max = 0


#server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#server.setsockopt(socket.SOL_SOCKET, 0x20, 1)

#server.bind(('', 40000))
p = Pin('PG12', Pin.OUT_PP, Pin.PULL_NONE)
np = neopixel.NeoPixel(p, 60)
n = np.n

#for i in range(n):
#    np[i] = (0,0,0)


#np.write()

while True:
#    m = 0
#    step = 0
#    print("here")
#    if (data == "close"):
#        greenLED.on()
#        redLED.off()
#        blueLED.off()
#    elif (data == "far"):
#        greenLED.off()
#        redLED.on(),
#        blueLED.off()
#    else:
#       print("nothing")
#       greenLED.off()
#       redLED.off()
#       blueLED.off()
#    print("i am here")
    evts = poller.poll(10) # .poll(millis)
#    if not evts:
#        print("No data recieved")
#        greenLED.on()
#        redLED.on()
    for sock, evt in evts:
#        print("here3")
        if evt and select.POLLIN:
            if sock == s:
                data, addr = s.recvfrom(1024)
                data = data.decode()
#                if (data == "short"):
#                    m = 3
#                    step = 2
#                    greenLED.on()
#                    redLED.off()
#                    blueLED.off()
#                elif (data == "medium"):
#                    m = 3
#                    step = 6
#                    print("medium")
#                    greenLED.off()
#                    redLED.on(),
#                    blueLED.off()
#                elif (data == "long"):
#                    m = 3
#                    step = 10
#                    print("long")
#                    greenLED.off()
#                    redLED.off(),
#                    blueLED.on()
#                elif (data == "change Mode"):
#                    m = 3
#                    step = 14
#                    print("change mode")
#                    greenLED.on()
#                    redLED.on(),
#                    blueLED.off()
                if (data == "none"):
                    print(data)
                    for i in range(n):
                        np[i] = (0, 0, 0)
                    np.write()
                elif (data == "X-axis pointing up"):
                    print(data)
                    redLED.on()
                    greenLED.off()
                    blueLED.off()
                    for i in range(n):
                        np[i] = (0, 100, 100)
                    np.write()

                elif (data == "X-axis pointing down"):
                    print(data)
                    redLED.off()
                    greenLED.off()
                    blueLED.on()
                    for i in range(n):
                        np[i] = (100, 0, 0)
                    np.write()
                elif (data == "Y-axis pointing up"):
                    print(data)
                    redLED.on()
                    greenLED.off()
                    blueLED.on()
                    for i in range(n):
                        np[i] = (0, 100, 0)
                    np.write()


                elif (data == "Y-axis pointing down"):
                    print(data)
                    redLED.on()
                    greenLED.on()
                    blueLED.off()
                    for i in range(n):
                        np[i] = (0, 0, 100)
                    np.write()

                elif (data == "Z-axis pointing up"):
                    print(data)
                    redLED.off()
                    greenLED.on()
                    blueLED.on()
                    for i in range(n):
                        np[i] = (100, 0, 100)
                    np.write()

                elif (data == "Z-axis pointing down"):
                    print(data)
                    redLED.off()
                    greenLED.off()
                    blueLED.off()
                    for i in range(n):
                        np[i] = (100, 100, 0)
                    np.write()
#                print(data)
#            if m > 0 and step > 0:
#                if data == "change Mode":
##                    n = 10
#                    for i in range(5):
#                        snake_length = 2
#                        snake_direction = 1
#                        snake_position = 0
#                        for snake_head_position in range(n + snake_length):
#                                np[j] = (0, 0, 128)  # Dim blue for all LEDs

#                            # Update the position of the snake's head
#                        for i in range(snake_length):
#                            # Calculate current position based on direction
#                            pos = (snake_position + i) % n

#                            # Light up the snake in a different color or turn off (if you want it dark)
#                            if 0 <= snake_head_position - i < n:
#                                np[pos] = (0, 0, 0)  # Turn off LEDs for the snake

#                        np.write()
#                        time.sleep_ms(200)

#                        # Move the snake
#                        snake_position += snake_direction
##                    for i in range(4 * n):
##                        for j in range(n):
##                            np[j] = (0, 0, 128)
##                        if (i // n) % 2 == 0:
##                            np[i % n] = (0, 0, 0)
##                        else:
##                            np[n - 1 - (i % n)] = (0, 0, 0)
##                        np.write()
##                        time.sleep_ms(60)
#                else:
#                    for _ in range(m):
#                        for i in range(0, 4 * 256, step):
#                            for j in range(n):
#                                if (i // 256) % 2 == 0:
#                                    val = i & 0xff
#                                else:
#                                    val = 255 - (i & 0xff)
#                                np[j] = (val, 0, 0)
#                            np.write()
#                        # Briefly check for new data without blocking
#                        evts = poller.poll(0)  # Non-blocking
#                        if evts:
#                            break  # Exit if new data is available to handle it immediately

#                    if evts:
#                        break

#            for i in range(n):
#                np[i] = (0, 0, 0)
#            np.write()

'''
                elif (data == "none"):
                    for i in range(n):
                        np[i] = (0, 0, 0)
                    np.write()
                elif (data == "X-axis pointing up"):
                    for i in range(n):
                        np[i] = (0, 100, 100)
                    np.write()

                elif (data == "X-axis pointing down"):
                    for i in range(n):
                        np[i] = (100, 0, 0)
                    np.write()


                elif (data == "Y-axis pointing up"):
                    for i in range(n):
                        np[i] = (0, 100, 0)
                    np.write()

                elif (data == "Y-axis pointing down"):
                    for i in range(n):
                        np[i] = (0, 0, 100)
                    np.write()


                elif (data == "Z-axis pointing up"):
                    for i in range(n):
                        np[i] = (100, 0, 100)
                    np.write()


                elif (data == "Z-axis pointing down"):
                    for i in range(n):
                        np[i] = (100, 100, 0)
                    np.write()
'''



