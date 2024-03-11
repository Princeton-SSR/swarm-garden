# This work is licensed under the MIT license.
# Copyright (c) 2013-2023 OpenMV LLC. All rights reserved.
# https://github.com/openmv/openmv/blob/master/LICENSE
#
# TensorFlow Lite Object Detection Example
#
# This examples uses the builtin FOMO model to detect faces.

import sensor
import time
import tf
import math
from machine import I2C
from vl53l1x import VL53L1X
import pyb
from machine import Pin
import select
from socket import *
import network, time
import time
import sys
# VL53L1X ToF sensor basic distance measurement example.
#from machine import I2C
from vl53l1x import VL53L1X
import time
from machine import Pin, SoftI2C
import pyb
import select

from pyb import Pin
import time
import sys
# VL53L1X ToF sensor basic distance measurement example.
from machine import I2C
from vl53l1x import VL53L1X
import time

tof = VL53L1X(I2C(2))

redLED = pyb.LED(1) # built-in red LED
greenLED = pyb.LED(2) # built-in green LED
blueLED = pyb.LED(3) # built-in blue LED

sensor.reset()  # Reset and initialize the sensor.
sensor.set_pixformat(sensor.RGB565)  # Set pixel format to RGB565 (or GRAYSCALE)
sensor.set_framesize(sensor.QVGA)  # Set frame size to QVGA (320x240)
sensor.set_windowing((240, 240))  # Set 240x240 window.
sensor.skip_frames(time=2000)  # Let the camera adjust.

min_confidence = 0.25

# Load built-in FOMO face detection model
labels, net = tf.load_builtin_model("fomo_face_detection")

# Alternatively, models can be loaded from the filesystem storage.
# net = tf.load('<object_detection_network>', load_to_fb=True)
# labels = [line.rstrip('\n') for line in open("labels.txt")]

colors = [  # Add more colors if you are detecting more than 7 types of classes at once.
    (255, 0, 0),
    (0, 255, 0),
    (255, 255, 0),
    (0, 0, 255),
    (255, 0, 255),
    (0, 255, 255),
    (255, 255, 255),
]



#out1 = 17
#out2 = 18
#out3 = 27
#out4 = 22

# careful lowering this, at some point you run into the mechanical limitation of how quick your motor can move
step_sleep = 0.003

step_count = 100

##400 is a full revolution and 0.003-0.006 step sleep is good

# setting up
#GPIO.setmode( GPIO.BCM )
#GPIO.setup( out1, GPIO.OUT )
#GPIO.setup( out2, GPIO.OUT )
#GPIO.setup( out3, GPIO.OUT )
#GPIO.setup( out4, GPIO.OUT )

out1 = Pin('PG12', Pin.OUT_PP, Pin.PULL_NONE)
out2 = Pin('PA9', Pin.OUT_PP, Pin.PULL_NONE)
out3 = Pin('PA10', Pin.OUT_PP, Pin.PULL_NONE)
out4 = Pin('PG1', Pin.OUT_PP, Pin.PULL_NONE)

# initializing
out1.value(0)
out2.value(0)
out3.value(0)
out4.value(0)

def cleanup():
    out1.value(0)
    out2.value(0)
    out3.value(0)
    out4.value(0)


tof = VL53L1X(I2C(2))
def upwards():
    for i in range(step_count):
        if i % 4 == 0:
            out1.value(1)
            out2.value(0)
            out3.value(0)
            out4.value(0)
        elif i % 4 == 1:
            out1.value(0)
            out2.value(0)
            out3.value(1)
            out4.value(0)
        elif i % 4 == 2:
            out1.value(0)
            out2.value(1)
            out3.value(0)
            out4.value(0)
        elif i % 4 == 3:
            out1.value(0)
            out2.value(0)
            out3.value(0)
            out4.value(1)

        time.sleep(step_sleep)

def downwards():
    for i in range(step_count):
        if i % 4 == 0:
            out1.value(0)
            out2.value(0)
            out3.value(0)
            out4.value(1)
        elif i % 4 == 1:
            out1.value(0)
            out2.value(1)
            out3.value(0)
            out4.value(0)
        elif i % 4 == 2:
            out1.value(0)
            out2.value(0)
            out3.value(1)
            out4.value(0)
        elif i % 4 == 3:
            out1.value(1)
            out2.value(0)
            out3.value(0)
            out4.value(0)

        time.sleep(step_sleep)

def stop():
    out1.value(0)
    out2.value(0)
    out3.value(0)
    out4.value(0)

max_steps = 48  # Set the maximum number of steps before stopping
clock = time.clock()
count = 0
while True:
    distance = tof.read()

    if distance <= 530:
        blueLED.off()
        redLED.on()

        clock.tick()

        img = sensor.snapshot()

        # detect() returns all objects found in the image (splitted out per class already)
        # we skip class index 0, as that is the background, and then draw circles of the center
        # of our objects

        for i, detection_list in enumerate(
            net.detect(img, thresholds=[(math.ceil(min_confidence * 255), 255)])

        ):

            if i == 0:
                continue  # background class
            if len(detection_list) == 0:
                greenLED.off()
                stop()
                continue  # no detections for this class?

            greenLED.on()

            if(count <= 48):
                upwards()
                count += 1
            for d in detection_list:
                [x, y, w, h] = d.rect()
                center_x = math.floor(x + (w / 2))
                center_y = math.floor(y + (h / 2))
                #print(f"x {center_x}\ty {center_y}")
                img.draw_circle((center_x, center_y, 12), color=colors[i], thickness=2)

    else:
        if(count >= 0):
            downwards()
            count -= 1

        blueLED.on()
        redLED.off()
        greenLED.off()


