import network
import omv
import rtsp
import sensor
import time
import sys
from pyb import Pin
from socket import *
import network
import time
import select
import utime
import uasyncio as asyncio
import pyb

sensor.reset()

#sensor.set_pixformat(sensor.BAYER)
#sensor.set_framesize(sensor.QVGA)
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.VGA)
sensor.__write_reg(0xf8, 0x8B)

omv.disable_fb(True)

redLED = pyb.LED(1) # built-in red LED
greenLED = pyb.LED(2) # built-in green LED
blueLED = pyb.LED(3) # built-in blue LED
data = ""

# Set up wifi network connection
network_if = network.WLAN(network.STA_IF)
network_if.active(True)
network_if.connect("BlueSwarm", "Tpossr236")
while not network_if.isconnected():
    print("Trying to connect. Note this may take a while...")
    time.sleep_ms(1000)


network_if.ifconfig(('192.168.0.246', '255.255.255.0', '192.168.0.1', '192.168.0.1'))

# Create socket that can broadcast
s = socket(AF_INET, SOCK_DGRAM)
s.setsockopt(SOL_SOCKET, 0x20, 1)
poller = select.poll()
poller.register(s, select.POLLIN)
# Bind to '' meaning we will listen for any message from any IP
# Bind to port 50000 so we can get messages sent to that port
s.bind(('', 50000))

# Setup RTSP Server
server = rtsp.rtsp_server(network_if, 15000)
blueLED.on()

# Callbacks and RTSP Server Registration
clock = time.clock()
def setup_callback(pathname, session):
    print('Opening "%s" in session %d' % (pathname, session))
def play_callback(pathname, session):
    clock.reset()
    clock.tick()
    print('Playing "%s" in session %d' % (pathname, session))
def pause_callback(pathname, session):  # VLC only pauses locally. This is never called.
    print('Pausing "%s" in session %d' % (pathname, session))
def teardown_callback(pathname, session):
    print('Closing "%s" in session %d' % (pathname, session))


server.register_setup_cb(setup_callback)
server.register_play_cb(play_callback)
server.register_pause_cb(pause_callback)
server.register_teardown_cb(teardown_callback)

# Called each time a new frame is needed.
def image_callback(pathname, session):
    img = sensor.snapshot()
    # Handle messages emitted from server
    evts = poller.poll(10) # .poll(millis)
    for sock, evt in evts:
        if evt and select.POLLIN:
            if sock == s:
                data, addr = s.recvfrom(1024)
                data = data.decode()
                if (data == "rightTilt"):
                        greenLED.on()
                        redLED.off()
                        blueLED.off()
                elif (data == "leftTilt"):
                        greenLED.off()
                        redLED.on(),
                        blueLED.off()
                elif (data == "neutral"):
                       greenLED.off()
                       redLED.off()
                       blueLED.on()
                else:
                       greenLED.off()
                       redLED.off()
                       blueLED.off()
    clock.tick()
    return img

#we may be able to remove the while true here but not sure yet
server.stream(image_callback, quality=70)


