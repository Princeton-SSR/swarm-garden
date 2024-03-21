from socket import *
import network, time
import time
import sys
# VL53L1X ToF sensor basic distance measurement example.
#from machine import I2C
from vl53l1x import VL53L1X
from vl53l0x import VL53L0X
import time
from machine import Pin, SoftI2C
import pyb
import select
import sensor
import tf

import neopixel
import mcp23017
from machine import I2C
from vl53l1x import VL53L1X

######################### SENSORS + BOARD STUFF #########################

redLED = pyb.LED(1) # built-in red LED
greenLED = pyb.LED(2) # built-in green LED
blueLED = pyb.LED(3) # built-in blue LED

sensor.reset()  # Reset and initialize the sensor.
sensor.set_pixformat(sensor.RGB565)  # Set pixel format to RGB565 (or GRAYSCALE)
sensor.set_framesize(sensor.QVGA)  # Set frame size to QVGA (320x240)
sensor.set_windowing((240, 240))  # Set 240x240 window.

min_confidence = 0.25

# Load built-in FOMO face detection model
labels, net = tf.load_builtin_model("fomo_face_detection")

colors = [  # Add more colors if you are detecting more than 7 types of classes at once.
    (255, 0, 0),
    (0, 255, 0),
    (255, 255, 0),
    (0, 0, 255),
    (255, 0, 255),
    (0, 255, 255),
    (255, 255, 255),
]

i2c = SoftI2C(scl=Pin('PB8', Pin.OUT_PP, Pin.PULL_NONE), sda=Pin('PB9'))
mcp = mcp23017.MCP23017(i2c, 0x22)


tof = VL53L1X(I2C(2)) # distance sensor
tof2 = VL53L0X(i2c, 0x29) # sensor on back of long screw for bloom treshold

#to change address of mcp,
#connect D0 to VCC -> 0x20 + 1= 0x21
#connect D1 to VCC -> 0x20 + 1= 0x22
#connect D2 to VCC -> 0x20 + 1= 0x24
#connect D0 and D1 to VCC -> 0x20 + 1 + 2= 0x23 etc

###############################################################################

########################## MODULE VARIABLES ###############################

# must match the id of the attached April Tag
module_ID = 2

# list of tuples where neighbor[0] = location, neighbor[1] = id ex. (topright, 4)
# updates on neighborsUpdate messages
neighbors_list = []

# current mode
mode = "idle"

# on board LED color
LEDcolor = ""

# how far the flower has bloomed, not sure if we need to track this here
#bloom = tof2.read()

# background LED strip color
LEDStripColor = "(0,0,0)"

# we will append this to the ifconfig to route camera streams properly
webhost_unique = str(200 + module_ID)

# used for checking when the last command was recieved
last_command_time = time.time()

#isBlooming = False

##########################################################################

################## SETTING UP WIFI NETWORK + SOCKET BROADCAST #################

SSID='BlueSwarm' # Network SSID
KEY='Tpossr236'  # Network key

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, KEY)
while not wlan.isconnected():
    print("Trying to connect. Note this may take a while...")
    time.sleep_ms(1000)


HOST ='192.168.0.' + webhost_unique

wlan.ifconfig((HOST, '255.255.255.0', '192.168.0.1', '192.168.0.1'))

blueLED.on() # visual indicator for successful wifi connection
# We should have a valid IP now via DHCP
print("WiFi Connected ", wlan.ifconfig())

# Setting up socket to listen for messages
s = socket(AF_INET, SOCK_DGRAM)
s.setsockopt(SOL_SOCKET, 0x20, 1)
poller = select.poll()
poller.register(s, select.POLLIN)

# Bind to '' meaning we will listen for any message from any IP
# Bind to PORT (50000 + module_ID) so we can recieve id-specific messages

s.bind(('', 50000 + module_ID))

################################################################################
time.sleep(5)
p = Pin('PG12', Pin.OUT_PP, Pin.PULL_NONE)
#p = machine.Pin.board.X8

np = neopixel.NeoPixel(p, 60)
n = np.n
### Draw a red gradient.
# Draw gradient
for i in range(n):
    np[i] = (0,0,0)

# Update the strip.
np.write()

# careful lowering this, at some point you run into the mechanical limitation of how quick your motor can move
step_sleep = 0.00305
current_motion = "stop"
step_count = 100

step_max = 0

# list interface
mcp[0].input()
mcp[1].input(pull=1)
mcp[1].value()
mcp[2].output(1)
mcp[3].output(0)
mcp[6].output(1)
# method interface
mcp.pin(0, mode=1)
#mcp.pin(0, mode=1, pullup=True)
mcp.pin(0, mode=1)
mcp.pin(1, mode=1)
mcp.pin(2, mode=1)
mcp.pin(3, mode=1)
mcp.pin(4, mode=1)
#mcp.pin(1, mode=0, value=1)
#mcp.pin(2, mode=0, value=0)

#mcp.pin(3, mode=1, pullup=True)
time.sleep(1)
#mcp.pin(3, mode=0, value=0)
#tof2 = VL53L0X(i2c, 0x29)
mcp.config(interrupt_polarity=0, interrupt_mirror=1)

# property interface 16-bit
#mcp.mode = 0xfffe
#mcp.gpio = 0x0001

# property interface 8-bit
#mcp.porta.mode = 0xfe
mcp.portb.mode = 0xff
mcp.porta.gpio = 0x01
mcp.portb.gpio = 0x02

##400 is a full revolution and 0.003-0.006 step sleep is good
mcp.pin(0, mode=0, value=0)
mcp.pin(1, mode=0, value=0)
mcp.pin(2, mode=0, value=0)
mcp.pin(3, mode=0, value=0)

def cleanup():
    mcp.pin(0, mode=0, value=0)
    mcp.pin(1, mode=0, value=0)
    mcp.pin(2, mode=0, value=0)
    mcp.pin(3, mode=0, value=0)

def downwards():
        for i in range(step_count):
            if i%4==0:
                mcp.pin(0, mode=0, value=1)
                mcp.pin(1, mode=0, value=0)
                mcp.pin(2, mode=0, value=0)
                mcp.pin(3, mode=0, value=0)

            elif i%4==1:
                mcp.pin(0, mode=0, value=0)
                mcp.pin(1, mode=0, value=0)
                mcp.pin(2, mode=0, value=1)
                mcp.pin(3, mode=0, value=0)

            elif i%4==2:
                mcp.pin(0, mode=0, value=0)
                mcp.pin(1, mode=0, value=1)
                mcp.pin(2, mode=0, value=0)
                mcp.pin(3, mode=0, value=0)
            elif i%4==3:
                mcp.pin(0, mode=0, value=0)
                mcp.pin(1, mode=0, value=0)
                mcp.pin(2, mode=0, value=0)
                mcp.pin(3, mode=0, value=1)
            time.sleep( step_sleep)

def upwards():
        for i in range(step_count):
            if i%4==0:
                mcp.pin(0, mode=0, value=0)
                mcp.pin(1, mode=0, value=0)
                mcp.pin(2, mode=0, value=0)
                mcp.pin(3, mode=0, value=1)
            elif i%4==1:
                mcp.pin(0, mode=0, value=0)
                mcp.pin(1, mode=0, value=1)
                mcp.pin(2, mode=0, value=0)
                mcp.pin(3, mode=0, value=0)
            elif i%4==2:
                mcp.pin(0, mode=0, value=0)
                mcp.pin(1, mode=0, value=0)
                mcp.pin(2, mode=0, value=1)
                mcp.pin(3, mode=0, value=0)
            elif i%4==3:
                mcp.pin(0, mode=0, value=1)
                mcp.pin(1, mode=0, value=0)
                mcp.pin(2, mode=0, value=0)
                mcp.pin(3, mode=0, value=0)
            time.sleep( step_sleep)

def stop():
    mcp.pin(0, mode=0, value=0)
    mcp.pin(1, mode=0, value=0)
    mcp.pin(2, mode=0, value=0)
    mcp.pin(3, mode=0, value=0)


########################### MESSAGE PARSER ##########################

def parse_message(message):
    parts = message.split()

    if len(parts) < 2:
        print("Incorrect message format")
        return "n/a", "n/a", None

    message_type = parts[0]
    sender_id = parts[1]
    content = {}

    for part in parts[2:]:
        key, value = part.split(":")
        content[key] = value

    return message_type, sender_id, content

###################################################################


##################### FORWARDING FUNCTIONS ########################

# takes in list of neighbors and LED strip color to propogate to neighbors
def forward_strip_to_neighbors(neighbors, rgb, incoming_rgb, prevSender):
    print(str(rgb))
    # for each neighbor, forward bloom message to their module_ID PORT
    for neighbor in neighbors:
        if neighbor[1] is not prevSender:
            sendData = "stripUpdate" + " " + str(module_ID) + " " + "rgb:" + incoming_rgb
            try:
                s.sendto(sendData.encode(), ('255.255.255.255', 50000 + int(neighbor[1])))
            except OSError as e:
                print("Error sending UDP message:", e)


def forward_strip_to_neighbors_direction(neighbors, rgb, incoming_rgb, prevSender, direction):
    print(str(rgb))
    # for each neighbor, forward bloom message to their module_ID PORT
    for neighbor in neighbors:
        if neighbor[1] is not prevSender and neighbor[0] is direction:
            sendData = "stripDirectionUpdate" + " " + str(module_ID) + " " + "rgb:" + incoming_rgb + " " + "direction:" + direction
            try:
                print(neighbor)
                s.sendto(sendData.encode(), ('255.255.255.255', 50000 + int(neighbor[1])))
            except OSError as e:
                print("Error sending UDP message:", e)


# takes in list of neighbors and bloom to propogate to neighbors
def forward_bloom_to_neighbors(neighbors, bloom, prevSender):

    # for each neighbor, forward bloom message to their module_ID PORT
    for neighbor in neighbors:
        if neighbor[1] is not prevSender:
            sendData = "bloomUpdate" + " " + str(module_ID) + " " + "bloom:" + bloom
            try:
                s.sendto(sendData.encode(), ('255.255.255.255', 50000 + int(neighbor[1])))
            except OSError as e:
                print("Error sending UDP message:", e)

# takes in list of neighbors and color to propogate to neighbors
def forward_LED_color_to_neighbors(neighbors, color, prevSender):

    # for each neighbor, forward color message to their module_ID PORT
    for neighbor in neighbors:
        if neighbor[1] is not prevSender:
            sendData = "LEDColorUpdate" + " " + str(module_ID) + " " + "color:" + color
            try:
                s.sendto(sendData.encode(), ('255.255.255.255', 50000 + int(neighbor[1])))
            except OSError as e:
                print("Error sending UDP message:", e)

# takes in list of neighbors and color to propogate to neighbors
def forward_LED_color_to_neighbors_direction(neighbors, color, prevSender, direction):

    # for each neighbor, forward color message to their module_ID PORT
    for neighbor in neighbors:
        if neighbor[1] is not prevSender and neighbor[0] is direction:
            sendData = "LEDColorDirectionUpdate" + " " + str(module_ID) + " " + "color:" + color + " " + "direction:" + direction
            try:
                print(neighbor)
                s.sendto(sendData.encode(), ('255.255.255.255', 50000 + int(neighbor[1])))
            except OSError as e:
                print("Error sending UDP message:", e)


########################### UPDATE HANDLING ##########################

def handle_neighbors_update(data):
    global neighbors_list

    message_type, sender_id, content = parse_message(data)
    neighbors_list = list(content.items())
    print("neighbors updated to: " + str(neighbors_list))

def handle_mode_update(data):
    global mode

    if "mpegPose" in data:
        mode = "mpegPose"
    elif "wearable" in data:
        mode = "wearable"
    else:
        mode = "idle"

def handle_LED_color_update(data):
    global LEDColor
    global neighbors_list

    message_type, sender_id, content = parse_message(data)
    incoming_color = content["color"]

    redLED.off()
    greenLED.off()
    blueLED.off()
    pyb.LED(int(incoming_color)).on()

    LEDColor = incoming_color
    forward_LED_color_to_neighbors(neighbors_list, incoming_color, sender_id)

def handle_bloom_update(data):
    global neighbors_list

    message_type, sender_id, content = parse_message(data)
    bloom = content["bloom"]

    dist_from_stop = tof2.read()

    if bloom is "unbloom":
        forward_bloom_to_neighbors(neighbors_list, bloom, sender_id)
        while dist_from_stop < 105:
            upwards()

            dist_from_stop = tof2.read()

    if bloom is "bloom":
        forward_bloom_to_neighbors(neighbors_list, bloom, sender_id)
        while dist_from_stop > 75:
            downwards()

            dist_from_stop = tof2.read()

    # right now this waits until complete bloom before sending but we will change
    #forward_bloom_to_neighbors(neighbors_list, bloom, sender_id)

    stop()

# Define the fading speed (in seconds)
FADE_SPEED = 0.05  # Adjust this value for the desired speed

def fade_color(old_color, new_color, fade_speed):
    """
    Fade from the old color to the new color gradually.
    """
    if old_color == new_color:
        return new_color

    # Convert string format to tuple of integers
    old_color = tuple(map(int, old_color[1:-1].split(',')))
    new_color = tuple(map(int, new_color[1:-1].split(',')))

    r_old, g_old, b_old = old_color
    r_new, g_new, b_new = new_color
    # Calculate the incremental steps for each color channel
    step_r = (r_new - r_old) / max(abs(r_new - r_old), 1)
    step_g = (g_new - g_old) / max(abs(g_new - g_old), 1)
    step_b = (b_new - b_old) / max(abs(b_new - b_old), 1)

    # Fade towards the new color gradually
    while (r_old, g_old, b_old) != new_color:
        r_old = int(r_old + step_r)
        g_old = int(g_old + step_g)
        b_old = int(b_old + step_b)
        yield (r_old, g_old, b_old)
        time.sleep(fade_speed)

def handle_strip_update(data):
    global LEDStripColor
    global neighbors_list

    message_type, sender_id, content = parse_message(data)
    incoming_rgb = content["rgb"]

    # Remove the outer parentheses and split the string into a list of strings
    rgb_values_str = incoming_rgb[1:-1].split(',')

    # Convert each string to an integer
    rgb = tuple(int(value) for value in rgb_values_str)


    for color in fade_color(LEDStripColor, incoming_rgb, FADE_SPEED):
           # Draw gradient
        for i in range(n):
            np[i] = color

        # Update the strip.
        np.write()

#    # Draw gradient
#    for i in range(n):
#        np[i] = rgb

#    # Update the strip.
#    np.write()

    LEDStripColor = incoming_rgb

    forward_strip_to_neighbors(neighbors_list, rgb, incoming_rgb, sender_id)


def handle_strip_direction_update(data):
    global LEDStripColor
    global neighbors_list

    message_type, sender_id, content = parse_message(data)
    incoming_rgb = content["rgb"]
    direction = content["direction"]

    # Remove the outer parentheses and split the string into a list of strings
    rgb_values_str = incoming_rgb[1:-1].split(',')

    # Convert each string to an integer
    rgb = tuple(int(value) for value in rgb_values_str)

    # Draw gradient
    for i in range(n):
        np[i] = rgb

    # Update the strip.
    np.write()

    LEDStripColor = incoming_rgb

    forward_strip_to_neighbors_direction(neighbors_list, rgb, incoming_rgb, sender_id, direction)


def handle_LED_color_direction_update(data):
    global LEDColor
    global neighbors_list

    message_type, sender_id, content = parse_message(data)
    incoming_color = content["color"]
    direction = content["direction"]

    redLED.off()
    greenLED.off()
    blueLED.off()
    pyb.LED(int(incoming_color)).on()

    LEDColor = incoming_color
    forward_LED_color_to_neighbors_direction(neighbors_list, incoming_color, sender_id, direction)


def return_to_base_conditions():
    # turn off LED strip
    for i in range(n):
        np[i] = (0,0,0)
    np.write()

    # set a global interrupt variable that can allow cut off mid-bloom?
    # lets try to also turn off listening here
    # reset to unbloom
#    dist_from_stop = tof2.read()

#    if dist_from_stop < 105:
#        while dist_from_stop < 105:
#            upwards()
#            dist_from_stop = tof2.read()


stabilize_time = 20  # seconds until return to base conditions runs

########################### IDLE MESSAGE LISTENING ##########################

def idle_listening(s):
    global neighbors_list
    global LEDColor
    global mode
    global last_command_time

    while True:
        evts = poller.poll(10)

        ##################### MESSAGE + STATE MANAGEMENT ######################
        for sock, evt in evts:
            if evt and select.POLLIN:
                if sock == s:
                    data, addr = s.recvfrom(1024)
                    data = data.decode()

                    last_command_time = time.time()

                    if "neighborsUpdate" in data:
                        handle_neighbors_update(data)
                    elif "modeUpdate" in data:
                        handle_mode_update(data)
                        return
                    elif "LEDColorUpdate" in data:
                        handle_LED_color_update(data)
                    elif "LEDColorDirectionUpdate" in data:
                        handle_LED_color_direction_update(data)
                    elif "bloomUpdate" in data:
                        handle_bloom_update(data)
                    elif "stripUpdate" in data:
                        handle_strip_update(data)
                    elif "stripDirectionUpdate" in data:
                        handle_strip_direction_update(data)

        # if no commands have happened in the last 20 seconds, return to base conditions
        if time.time() - last_command_time >= stabilize_time:
                #stop listening
                return_to_base_conditions()
                #continue listening


##################@### WEBSERVER SOCKET + STREAMING / LISTENING ################

WEBPORT = 8080 + module_ID

# Create server socket
webserver = socket(AF_INET, SOCK_STREAM)
webserver.setsockopt(SOL_SOCKET, SO_REUSEADDR, True)

# Bind and listen
webserver.bind([HOST, WEBPORT])
webserver.listen(5)

# Set server socket to blocking
webserver.setblocking(True)

###############################################################################

#################### MPEG STREAMING TO WEBSERVER ##############################

def MPEG_streaming(s, webserver):
    global neighbors_list
    global LEDColor
    global module_ID
    global mode
    global last_command_time

    print("Waiting for connections..")
    client, addr = webserver.accept()
    # set client socket timeout to 5s
    client.settimeout(5.0) # might have to change this
    print("Connected to " + addr[0] + ":" + str(addr[1]))

    # Read request from client
    img_data = client.recv(1024)
    # Should parse client request here

    # Send multipart header
    client.sendall(
        "HTTP/1.1 200 OK\r\n"
        "Server: OpenMV\r\n"
        "Content-Type: multipart/x-mixed-replace;boundary=openmv\r\n"
        "Cache-Control: no-cache\r\n"
        "Pragma: no-cache\r\n\r\n"
    )

    # Start streaming images
    # NOTE: Disable IDE preview to increase streaming FPS.
    while True:

        #clock.tick()  # Track elapsed milliseconds between snapshots().
        frame = sensor.snapshot()
        cframe = frame.compressed(quality=35)
        header = (
            "\r\n--openmv\r\n"
            "Content-Type: image/jpeg\r\n"
            "Content-Length:" + str(cframe.size()) + "\r\n\r\n"
        )
        client.sendall(header)
        client.sendall(cframe)

        evts = poller.poll(10)

        ##################### MESSAGE + STATE MANAGEMENT ######################
        for sock, evt in evts:
            if evt and select.POLLIN:
                if sock == s:
                    data, addr = s.recvfrom(1024)
                    data = data.decode()

                    last_command_time = time.time()

                    if "neighborsUpdate" in data:
                        handle_neighbors_update(data)
                    elif "modeUpdate" in data:
                        handle_mode_update(data)
                        return
                    elif "LEDColorUpdate" in data:
                        handle_LED_color_update(data)
                    elif "LEDColorDirectionUpdate" in data:
                        handle_LED_color_direction_update(data)
                    elif "bloomUpdate" in data:
                        handle_bloom_update(data)
                    elif "stripUpdate" in data:
                        handle_strip_update(data)
                    elif "stripDirectionUpdate" in data:
                        handle_strip_direction_update(data)

        # if no commands have happened in the last 20 seconds, return to base conditions
        if time.time() - last_command_time >= stabilize_time:
                return_to_base_conditions()


###############################################################################

while(True):

    ##################### MODE MANAGEMENT ######################
    if mode == "mpegPose":
        try:
           MPEG_streaming(s, webserver)
        except:
            print("Reconnect Camera")
    elif mode == "wearable":
        print("wearable")
    else:
        idle_listening(s)
