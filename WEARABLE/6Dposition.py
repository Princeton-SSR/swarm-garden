# This work is licensed under the MIT license.
# Copyright (c) 2013-2023 OpenMV LLC. All rights reserved.
# https://github.com/openmv/openmv/blob/master/LICENSE
#
# LSM6DSOX IMU MLC (Machine Learning Core) Example.
# Download the raw UCF file, copy to storage and reset.

# NOTE: The pre-trained models (UCF files) for the examples can be found here:
# https://github.com/STMicroelectronics/STMems_Machine_Learning_Core/tree/master/application_examples/lsm6dsox

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

INT_MODE = True  # Run in interrupt mode.
INT_FLAG = False  # Set True on interrupt.

redLED = pyb.LED(1) # built-in red LED
greenLED = pyb.LED(2) # built-in green LED
blueLED = pyb.LED(3) # built-in blue LED

network_if = network.WLAN(network.STA_IF)
network_if.active(True)
network_if.connect("SwarmGarden", "swarmgardenhorray123!")
while not network_if.isconnected():
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

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.setsockopt(socket.SOL_SOCKET, 0x20, 1)
# Enable broadcasting mode
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.setsockopt(socket.SOL_SOCKET, 0x20, 1)
server.bind(("", 30000))

def imu_int_handler(pin):
    global INT_FLAG
    INT_FLAG = True


if INT_MODE is True:
    int_pin = Pin("PA1", mode=Pin.IN, pull=Pin.PULL_UP)
    int_pin.irq(handler=imu_int_handler, trigger=Pin.IRQ_RISING)

# Vibration detection example
UCF_FILE = "lsm6dsox_six_d_position.ucf"
UCF_LABELS = {0: "none", 1: "X-axis pointing up", 2: "X-axis pointing down", 3: "Y-axis pointing up", 4: "Y-axis pointing down", 5: "Z-axis pointing up", 6: "Z-axis pointing down"}
# NOTE: Selected data rate and scale must match the MLC data rate and scale.
lsm = LSM6DSOX(
    SPI(5),
    cs=Pin("PF6", Pin.OUT_PP, Pin.PULL_UP),
    gyro_odr=26,
    accel_odr=26,
    gyro_scale=2000,
    accel_scale=4,
    ucf=UCF_FILE,
)

# Head gestures example
# UCF_FILE = "lsm6dsox_head_gestures.ucf"
# UCF_LABELS = {0:"Nod", 1:"Shake", 2:"Stationary", 3:"Swing", 4:"Walk"}
# NOTE: Selected data rate and scale must match the MLC data rate and scale.
# lsm = LSM6DSOX(SPI(5), cs_pin=Pin("PF6", Pin.OUT_PP, Pin.PULL_UP),
#        gyro_odr=26, accel_odr=26, gyro_scale=250, accel_scale=2, ucf=UCF_FILE)

print("MLC configured...")

while True:
    sendData = ""
    if INT_MODE:
        if INT_FLAG:
            INT_FLAG = False
            mlc_output = lsm.mlc_output()
            if mlc_output is not None and UCF_LABELS[mlc_output[0]] is not None:
                sendData = UCF_LABELS[lsm.mlc_output()[0]]
#                print(UCF_LABELS[mlc_output[0]])
#                if (sendData == "none"):
#                    redLED.off()
#                    greenLED.on()
#                    blueLED.off()
                if (sendData == "X-axis pointing up"):
                    redLED.on()
                    greenLED.off()
                    blueLED.off()

                elif (sendData == "X-axis pointing down"):
                    redLED.off()
                    greenLED.off()
                    blueLED.on()
                elif (sendData == "Y-axis pointing up"):
                    redLED.on()
                    greenLED.off()
                    blueLED.on()

                elif (sendData == "Y-axis pointing down"):
                    redLED.on()
                    greenLED.on()
                    blueLED.off()

                elif (sendData == "Z-axis pointing up"):
                    redLED.off()
                    greenLED.on()
                    blueLED.on()

                elif (sendData == "Z-axis pointing down"):
                    redLED.off()
                    greenLED.off()
                    blueLED.off()

            else:
                sendData = "none"
                redLED.off()
                greenLED.on()
                blueLED.off()
            print(sendData)


#            if UCF_LABELS[lsm.mlc_output()[0]] == None:
#                sendData = "None"
##            sendData = UCF_LABELS[lsm.mlc_output()[0]]
#            print(UCF_LABELS[lsm.mlc_output()[0]])
    else:
        print("here")
#        buf = lsm.mlc_output()
#        if buf is not None and UCF_LABELS[buf[0]] is not None:
#            sendData = UCF_LABELS[buf[0]]
#            print(sendData)

    if sendData == "none":
        continue
    else:
        server.sendto(sendData.encode(), ('255.255.255.255', 40000))
        server.sendto(sendData.encode(), ('255.255.255.255', 40000))
        server.sendto(sendData.encode(), ('255.255.255.255', 40000))
        server.sendto(sendData.encode(), ('255.255.255.255', 40000))
