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
import random

######################### SENSORS + BOARD STUFF #########################

redLED = pyb.LED(1) # built-in red LED
greenLED = pyb.LED(2) # built-in green LED
blueLED = pyb.LED(3) # built-in blue LED

sensor.reset()  # Reset and initialize the sensor.
sensor.set_pixformat(sensor.RGB565)  # Set pixel format to RGB565 (or GRAYSCALE)
sensor.set_framesize(sensor.QVGA)  # Set frame size to QVGA (320x240)
sensor.set_windowing((240, 240))  # Set 240x240 window.


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

def read_module_info(filename):
    module_info = {}
    with open(filename, 'r') as file:
        for line in file:
            # Split each line into key-value pairs
            info = line.strip().split(',')
            module_id = None
            module_data = {}
            for item in info:
                key, value = item.split(':')
                if key == 'module_ID':
                    module_id = int(value)
                else:
                    module_data[key] = value
            if module_id is not None:
                module_info[module_id] = module_data
    return module_info

module_info = read_module_info('module_info.txt')

def get_module_info(module_id):
    return module_info.get(module_id, {})

# must match the id of the attached April Tag
module_ID = 33

info = get_module_info(module_ID)

# blooming thresholds for tof2 sensor
unbloom_thresh = int(info["unbloom_thresh"])
bloom_thresh = int(info["bloom_thresh"])

# shimstock sheet color: orange, yellow, or red
sheetColor = str(info["sheetColor"])

print("module_ID:", module_ID, "unbloom_thresh:", unbloom_thresh, "bloom_thresh:", bloom_thresh, "sheetColor:", sheetColor)

# list of tuples where neighbor[0] = location, neighbor[1] = id ex. (topright, 4)
# updates on neighborsUpdate messages
neighbors_list = []

# current mode
mode = "idle"

# on board LED color (starts as blue (3) after wifi connection)
LEDColor = "3"

# how far the flower has bloomed, not sure if we need to track this here
#bloom = tof2.read()

# background LED strip color
LEDStripColor = "(0,0,0)"

# we will append this to the  to route camera streams properly
webhost_unique = str(200 + module_ID)

# used for checking when the last command was recieved
last_command_time = time.time()

# used for turning off and on listening
listeningOn = True

# global paint vars used for light painting mode
current_paint = '(100,0,0)'
paint_palette = ['(100,0,0)','(100,0,100)','(0,100,100)','(100,100,0)', '(50,100,0)']
iteration = 0

# used to make messages unique to ensure no doubly received states, reduces settle time
curr_msg_id = "Z"

##########################################################################

################## SETTING UP WIFI NETWORK + SOCKET BROADCAST #################

SSID='SwarmGarden' # Network SSID
KEY='swarmgardenhorray123!'  # Network key

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, KEY)
while not wlan.isconnected():
    print("Trying to connect. Note this may take a while...")
    time.sleep_ms(1000)


HOST = '192.168.2.134'

wlan.ifconfig((HOST, '255.255.255.0', '192.168.2.1', '192.168.2.1'))

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
step_sleep = 0.005
step_count = 200

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

            evts = poller.poll(0)

            for sock, evt in evts:
                if evt and select.POLLIN:
                    if sock == s:
                        data, addr = s.recvfrom(1024)
                        data = data.decode()

                        if "neighborsUpdate" in data:
                            handle_neighbors_update(data)
                        elif "modeUpdate" in data:
                            handle_mode_update(data)
                            return
                        elif "bloomUpdate" in data:
                            handle_bloom_update(data)
                        elif "stripUpdate" in data:
                            handle_strip_update(data)
                        elif "stripDirectionUpdate" in data:
                            handle_strip_direction_update(data)
                        elif "bloomSelf" in data:
                            handle_bloom_self(data)
                        elif "stripSelf" in data:
                            handle_strip_self(data)

            time.sleep(step_sleep)

        return True

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

            evts = poller.poll(0)

            for sock, evt in evts:
                if evt and select.POLLIN:
                    if sock == s:
                        data, addr = s.recvfrom(1024)
                        data = data.decode()

                        if "neighborsUpdate" in data:
                            handle_neighbors_update(data)
                        elif "modeUpdate" in data:
                            handle_mode_update(data)
                            return
                        elif "bloomUpdate" in data:
                            handle_bloom_update(data)
                        elif "stripUpdate" in data:
                            handle_strip_update(data)
                        elif "stripDirectionUpdate" in data:
                            handle_strip_direction_update(data)
                        elif "bloomSelf" in data:
                            handle_bloom_self(data)
                        elif "stripSelf" in data:
                            handle_strip_self(data)

            time.sleep(step_sleep)

        return True

def upwards_listen_off():
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

            time.sleep(step_sleep)

def downwards_listen_off():
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

            time.sleep(step_sleep)


def stop():
    mcp.pin(0, mode=0, value=0)
    mcp.pin(1, mode=0, value=0)
    mcp.pin(2, mode=0, value=0)
    mcp.pin(3, mode=0, value=0)


########################### MESSAGE PARSER ##########################
def generate_random_id(length=6):
    digits = '0123456789'
    return ''.join(random.choice(digits) for _ in range(length))


def parse_message(message):
    parts = message.split()

    if len(parts) < 2:
        print("Incorrect message format")
        return "n/a", "n/a", None

    message_type = parts[0]
    sender_id_string = parts[1]
    message_unique_id = parts[2]
    prev_senders = []
    content = {}

    prev_senders = sender_id_string.split(",")

    for part in parts[3:]:
        key, value = part.split(":")
        content[key] = value

    return message_type, sender_id_string, prev_senders, message_unique_id, content


###################################################################


##################### FORWARDING FUNCTIONS ########################

# takes in list of neighbors and LED strip color to propogate to neighbors
def forward_strip_to_neighbors(neighbors, incoming_rgb, sender_id_string, prev_senders):
    global module_ID
    global curr_msg_id

    print(prev_senders)
    # for each neighbor, forward bloom message to their module_ID PORT
    for neighbor in neighbors:
        if neighbor[1] not in prev_senders:
            if neighbor[0] is not 'far':
                sendData = "stripUpdate" + " " + sender_id_string + "," + str(module_ID) + " " + curr_msg_id + " " + "rgb:" + incoming_rgb
                print(sendData + " to module:" + neighbor[1])
                try:
                    s.sendto(sendData.encode(), ('255.255.255.255', 50000 + int(neighbor[1])))
                except OSError as e:
                    print("Error sending UDP message:", e)

def forward_strip_to_neighbors_direction(neighbors, rgb, incoming_rgb, sender_id_string, prev_senders, direction):
    global module_ID

    # for each neighbor, forward bloom message to their module_ID PORT
    for neighbor in neighbors:
        if neighbor[1] not in prev_senders:
            if neighbor[0] == direction:
                sendData = "stripDirectionUpdate" + " " + sender_id_string + "," + str(module_ID) + " " + curr_msg_id + " " + "rgb:" + incoming_rgb + " " + "direction:" + direction
                print(sendData + " to module:" + neighbor[1])
                try:
                    s.sendto(sendData.encode(), ('255.255.255.255', 50000 + int(neighbor[1])))
                except OSError as e:
                    print("Error sending UDP message:", e)

# takes in list of neighbors and bloom to propogate to neighbors
def forward_bloom_to_neighbors(neighbors, bloom, sender_id_string, prev_senders):
    global module_ID

    # for each neighbor, forward bloom message to their module_ID PORT
    for neighbor in neighbors:
        if neighbor[1] not in prev_senders:
            if neighbor[0] is not 'far':
                sendData = "bloomUpdate" + " " + sender_id_string + "," + str(module_ID) + " " + curr_msg_id + " " + "bloom:" + bloom
                print(sendData + " to module:" + neighbor[1])
                try:
                    s.sendto(sendData.encode(), ('255.255.255.255', 50000 + int(neighbor[1])))
                except OSError as e:
                    print("Error sending UDP message:", e)

# takes in list of neighbors and color to propogate to neighbors
def forward_LED_color_to_neighbors(neighbors, color, sender_id_string, prev_senders):
    global module_ID

    # for each neighbor, forward color message to their module_ID PORT
    for neighbor in neighbors:
        if neighbor[1] not in prev_senders:
            if neighbor[0] is not 'far':
                sendData = "LEDColorUpdate" + " " + sender_id_string + "," + str(module_ID) + " " + curr_msg_id + " " + "color:" + color
                print(sendData + " to module:" + neighbor[1])
                try:
                    s.sendto(sendData.encode(), ('255.255.255.255', 50000 + int(neighbor[1])))
                except OSError as e:
                    print("Error sending UDP message:", e)

# takes in list of neighbors and color to propogate to neighbors
def forward_LED_color_to_neighbors_direction(neighbors, color, sender_id_string, prev_senders, direction):
    global module_ID

    # for each neighbor, forward color message to their module_ID PORT
    for neighbor in neighbors:
        if neighbor[1] not in prev_senders:
             if neighbor[0] == direction:
                sendData = "LEDColorDirectionUpdate" + " " + sender_id_string + "," + str(module_ID) + " " + curr_msg_id + " " + "color:" + color + " " + "direction:" + direction
                print(sendData + " to module:" + neighbor[1])
                try:
                    print(neighbor)
                    s.sendto(sendData.encode(), ('255.255.255.255', 50000 + int(neighbor[1])))
                except OSError as e:
                    print("Error sending UDP message:", e)


########################### UPDATE HANDLING ##########################

def handle_neighbors_update(data):
    global neighbors_list

    message_type, sender_id_string, prev_senders, incoming_msg_id, content = parse_message(data)
    neighbors_list = list(content.items())
    print("neighbors updated to: " + str(neighbors_list))

def handle_mode_update(data):
    global mode

    if "mpegPose" in data:
        mode = "mpegPose"
    elif "wearable" in data:
        mode = "wearable"
    elif "proximityColor" in data:
        mode = "proximityColor"
    elif "lightPainting" in data:
        mode = "lightPainting"
    elif "proximityBloom" in data:
        mode = "proximityBloom"
    elif "proximityTransient" in data:
        mode = "proximityTransient"
    else:
        mode = "idle"

def handle_LED_color_update(data):
    global LEDColor
    global neighbors_list
    global curr_msg_id

    message_type, sender_id_string, prev_senders, incoming_msg_id, content = parse_message(data)

    incoming_color = content["color"]
    # if i have already recieved a message with this unique id, don't do anything
    if incoming_msg_id == curr_msg_id:
        print("rejected duplicate message: " + data)
        return

    # if i'm already a previous sender of this info don't do anything
    for prev in prev_senders:
        if str(module_ID) == prev:
            print("rejected backpropped message: " + data)
            return

    redLED.off()
    greenLED.off()
    blueLED.off()
    pyb.LED(int(incoming_color)).on()

    LEDColor = incoming_color
    forward_LED_color_to_neighbors(neighbors_list, incoming_color, sender_id_string, prev_senders)

def handle_bloom_update(data):
    global neighbors_list
    global bloom_thresh
    global unbloom_thresh
    global listeningOn
    global curr_msg_id

    message_type, sender_id_string, prev_senders, incoming_msg_id, content = parse_message(data)
    bloom = content["bloom"]

    # if i have already recieved a message with this unique id, don't do anything
    if incoming_msg_id == curr_msg_id:
        print("rejected duplicate message: " + data)
        return

    # if i'm already a previous sender of this info don't do anything
    for prev in prev_senders:
        if str(module_ID) == prev:
            print("rejected backpropped message: " + data)
            return

    dist_from_stop = tof2.read()

    if bloom is "unbloom":
        while dist_from_stop < unbloom_thresh:
            listeningOn = False

            check = upwards()

            if check == False:
                listeningOn = True
                stop()
                return()

            # at the halfway point propagate
            if ((unbloom_thresh + bloom_thresh) // 2) - 2 <= dist_from_stop <= ((unbloom_thresh + bloom_thresh) // 2) + 2:
                print('unbloom sent')
                forward_bloom_to_neighbors(neighbors_list, bloom, sender_id_string, prev_senders)

            dist_from_stop = tof2.read()

    if bloom is "bloom":
        while dist_from_stop > bloom_thresh:
            listeningOn = False

            check = downwards()

            if check == False:
                listeningOn = True
                stop()
                return()

            # at the halfway point propagate
            if ((unbloom_thresh + bloom_thresh) // 2) - 2 <= dist_from_stop <= ((unbloom_thresh + bloom_thresh) // 2) + 2:
                print('bloom sent')
                forward_bloom_to_neighbors(neighbors_list, bloom, sender_id_string, prev_senders)

            dist_from_stop = tof2.read()

    listeningOn = True
    stop()

# Define the fading speed (in seconds)
#FADE_SPEED = 0.01  # Adjust this value for the desired speed

def fade_color(old_color, new_color):
    """
    Fade from the old color to the new color gradually.
    """

    # Convert string format to tuple of integers
    old_color = tuple(map(int, old_color[1:-1].split(',')))
    new_color = tuple(map(int, new_color[1:-1].split(',')))

    r_old, g_old, b_old = old_color
    r_new, g_new, b_new = new_color

    if old_color == new_color:
        return [new_color]

    # Calculate the total number of steps needed
    num_steps = max(abs(r_new - r_old), abs(g_new - g_old), abs(b_new - b_old))

    # Ensure we have at least one step
    num_steps = max(num_steps, 1)

    # Calculate the incremental steps for each color channel
    step_r = (r_new - r_old) / num_steps
    step_g = (g_new - g_old) / num_steps
    step_b = (b_new - b_old) / num_steps

    # Generate color steps
    color_steps = [(int(r_old + i * step_r), int(g_old + i * step_g), int(b_old + i * step_b)) for i in range(num_steps)]

    return color_steps

def handle_strip_update(data):
    global LEDStripColor
    global neighbors_list
    global listeningOn
    global curr_msg_id

    message_type, sender_id_string, prev_senders, incoming_msg_id, content = parse_message(data)
    incoming_rgb = content["rgb"]

    # if i have already recieved a message with this unique id, don't do anything
    if incoming_msg_id == curr_msg_id:
        print("rejected duplicate message: " + data)
        return

    # if i'm already a previous sender of this info don't do anything
    for prev in prev_senders:
        if str(module_ID) == prev:
            print("rejected backpropped message: " + data)
            return

    print("accepted message: " + data)
    # adopt the incoming unique message id
    curr_msg_id = incoming_msg_id

    # Remove the outer parentheses and split the string into a list of strings
    rgb_values_str = incoming_rgb[1:-1].split(',')

    # Convert each string to an integer
    rgb = tuple(int(value) for value in rgb_values_str)

    # Define the fading speed (in seconds)
    FADE_SPEED = 0.005  # Adjust this value for the desired speed

    for color in fade_color(LEDStripColor, incoming_rgb):
           # Draw gradient
        for i in range(n):
            np[i] = color
        # Update the strip.
        np.write()
        time.sleep(FADE_SPEED)

    LEDStripColor = incoming_rgb

    forward_strip_to_neighbors(neighbors_list, incoming_rgb, sender_id_string, prev_senders)

def handle_strip_direction_update(data):
    global LEDStripColor
    global neighbors_list
    global listeningOn
    global curr_msg_id

    message_type, sender_id_string, prev_senders, incoming_msg_id, content = parse_message(data)
    incoming_rgb = content["rgb"]
    direction = content["direction"]

    # if i have already recieved a message with this unique id, don't do anything
    if incoming_msg_id == curr_msg_id:
        print("rejected duplicate message: " + data)
        return

    # if i'm already a previous sender of this info don't do anything
    for prev in prev_senders:
        if str(module_ID) == prev:
            print("rejected backpropped message: " + data)
            return

    # Remove the outer parentheses and split the string into a list of strings
    rgb_values_str = incoming_rgb[1:-1].split(',')

    # Convert each string to an integer
    rgb = tuple(int(value) for value in rgb_values_str)

    # Define the fading speed (in seconds)
    FADE_SPEED = 0.01  # Adjust this value for the desired speed

    for color in fade_color(LEDStripColor, incoming_rgb):
           # Draw gradient
        for i in range(n):
            np[i] = color
        # Update the strip.
        np.write()
        time.sleep(FADE_SPEED)

    LEDStripColor = incoming_rgb

    forward_strip_to_neighbors_direction(neighbors_list, rgb, incoming_rgb, sender_id_string, prev_senders, direction)

def handle_LED_color_direction_update(data):
    global LEDColor
    global neighbors_list
    global curr_msg_id

    message_type, sender_id_string, prev_senders, incoming_msg_id, content = parse_message(data)
    incoming_color = content["color"]
    direction = content["direction"]

    # if i have already recieved a message with this unique id, don't do anything
    if incoming_msg_id == curr_msg_id:
        print("rejected duplicate message: " + data)
        return

    # if i'm already a previous sender of this info don't do anything
    for prev in prev_senders:
        if str(module_ID) == prev:
            print("rejected backpropped message: " + data)
            return

    redLED.off()
    greenLED.off()
    blueLED.off()
    pyb.LED(int(incoming_color)).on()

    LEDColor = incoming_color
    forward_LED_color_to_neighbors_direction(neighbors_list, incoming_color, sender_id_string, prev_senders, direction)


def handle_expand(data):
    global LEDStripColor
    global neighbors_list
    global module_ID
    global curr_msg_id

    print("handle_expand")

    # Parse the received data to get the LED color, if necessary
    message_type, sender_id_string, prev_senders, incoming_msg_id, content = parse_message(data)

    # Extract the current LED color if sent within the data or use the global one
    incoming_rgb = content["rgb"]
    expand = content["expand"]

    # Remove the outer parentheses and split the string into a list of strings
    rgb_values_str = incoming_rgb[1:-1].split(',')

    # Convert each string to an integer
    rgb = tuple(int(value) for value in rgb_values_str)

    if expand == "short":
        print("short expand")
        handle_strip_self("stripSelf X X rgb:" + incoming_rgb)
        return

    elif expand == "medium":
        print("medium expand")

        handle_strip_self("stripSelf X X rgb:" + incoming_rgb)
        curr_msg_id = generate_random_id(6)
        for neighbor in neighbors_list:
            for prev in prev_senders:
                if neighbor[1] != prev:
                    if neighbor[0] is not 'far':
                        sendData = "stripSelf" + " " + sender_id_string + "," + str(module_ID) + " " + curr_msg_id + " " + "rgb:" + incoming_rgb
                        print(sendData + " to module:" + neighbor[1])
                        try:
                            s.sendto(sendData.encode(), ('255.255.255.255', 50000 + int(neighbor[1])))
                        except OSError as e:
                            print("Error sending UDP message:", e)

    elif expand == "long":
        print("long expand")
        handle_strip_self("stripSelf X X rgb:" + incoming_rgb)
        forward_strip_to_neighbors(neighbors_list, incoming_rgb, sender_id_string, prev_senders)
    else:
        for i in range(n):
            np[i] = (0, 0, 0)
        np.write()


##### Changing module state variables without propagation #####

def handle_bloom_self(data):
    global bloom_thresh
    global unbloom_thresh
    global listeningOn

    message_type, sender_id_string, prev_senders, incoming_msg_id, content = parse_message(data)

    bloom = content["bloom"]

    dist_from_stop = tof2.read()

    if bloom is "unbloom":
        while dist_from_stop < unbloom_thresh:
            listeningOn = False

            upwards_listen_off()

            dist_from_stop = tof2.read()

    if bloom is "bloom":
        while dist_from_stop > bloom_thresh:
            listeningOn = False

            downwards_listen_off()

            dist_from_stop = tof2.read()

    listeningOn = True
    stop()

    return


def handle_strip_self(data):
    global LEDStripColor

    message_type, sender_id_string, prev_senders, incoming_msg_id, content = parse_message(data)
    incoming_rgb = content["rgb"]

    # Remove the outer parentheses and split the string into a list of strings
    rgb_values_str = incoming_rgb[1:-1].split(',')

    # Convert each string to an integer
    rgb = tuple(int(value) for value in rgb_values_str)

    # Define the fading speed (in seconds)
    FADE_SPEED = 0.01  # Adjust this value for the desired speed

    for color in fade_color(LEDStripColor, incoming_rgb):
           # Draw gradient
        for i in range(n):
            np[i] = color
        # Update the strip.
        np.write()
        time.sleep(FADE_SPEED)

    LEDStripColor = incoming_rgb

    return

def handle_strip_paint(data):
    global LEDStripColor

    message_type, sender_id_string, prev_senders, incoming_msg_id, content = parse_message(data)
    incoming_rgb = content["rgb"]

    # Remove the outer parentheses and split the string into a list of strings
    rgb_values_str = incoming_rgb[1:-1].split(',')

    # Convert each string to an integer
    rgb = tuple(int(value) for value in rgb_values_str)

    # Define the fading speed (in seconds)
    FADE_SPEED = 0.01  # Adjust this value for the desired speed

    for color in fade_color(LEDStripColor, incoming_rgb):
           # Draw gradient
        for i in range(n):
            np[i] = color
        # Update the strip.
        np.write()
        time.sleep(FADE_SPEED)

    return

def handle_pulse(data):
    m = 0
    step = 0
    global LEDStripColor

    p = Pin('PG12', Pin.OUT_PP, Pin.PULL_NONE)
    np = neopixel.NeoPixel(p, 60)
    n = np.n

    message_type, sender_id_string, prev_senders, incoming_msg_id, content = parse_message(data)

    incoming_rgb = content["rgb"]

    pulse = content["pulse"]

    if LEDStripColor == incoming_rgb:
        return
    # Remove the outer parentheses and split the string into a list of strings
    rgb_values_str = incoming_rgb[1:-1].split(',')

    # Convert each string to an integer
    rgb = tuple(int(value) for value in rgb_values_str)

    # Define the fading speed (in seconds)

    if (pulse == "short"):
        m = 3
        step = 2
        print("short")
    elif (pulse == "medium"):
        m = 3
        step = 6
        print("medium")
    elif (pulse == "long"):
        m = 3
        step = 10
        print("long")
#    elif (pulse == "changeMode"):
#        m = 3
#        step = 14
#        print("change mode")

    for _ in range(m):
        for i in range(0, 4 * 256, step):
            for j in range(n):
                if (i // 256) % 2 == 0:
                    val = i & 0xff
                else:
                    val = 255 - (i & 0xff)
                np[j] = (val, 0, 0)
            np.write()
        evts = poller.poll(0)  # Non-blocking
        if evts:
            break  # Exit if new data is available to handle it immediately

    for i in range(n):
        np[i] = (0, 0, 0)
    np.write()


    LEDStripColor = "(0, 0, 0)"

    return

def handle_imu(data):
    global LEDStripColor
    global neighbors_list
    global module_ID
    global curr_msg_id

    print("handle_imu")

    message_type, sender_id_string, prev_senders, incoming_msg_id, content = parse_message(data)
    curr_msg_id = incoming_msg_id
    incoming_rgb = content["rgb"]

    direction = content["direction"]

    # Remove the outer parentheses and split the string into a list of strings
    rgb_values_str = incoming_rgb[1:-1].split(',')

    # Convert each string to an integer
    rgb = tuple(int(value) for value in rgb_values_str)

    # Define the fading speed (in seconds)

    if (direction == "x-axis-up"):
        print("x up")
        handle_strip_self("stripSelf X X rgb:" + incoming_rgb)
        LEDStripColor = incoming_rgb
        forward_strip_to_neighbors(neighbors_list, incoming_rgb, sender_id_string, prev_senders)
    elif (direction == "z-axis-up"):
        print("z up")
        handle_strip_self("stripSelf X X rgb:" + incoming_rgb)
        LEDStripColor = incoming_rgb
        forward_strip_to_neighbors_direction(neighbors_list, rgb, incoming_rgb, sender_id_string, prev_senders, "topright")
        forward_strip_to_neighbors_direction(neighbors_list, rgb, incoming_rgb, sender_id_string, prev_senders, "bottomright")
    elif (direction == "z-axis-down"):
        print("z down")
        handle_strip_self("stripSelf X X rgb:" + incoming_rgb)
        LEDStripColor = incoming_rgb
        forward_strip_to_neighbors_direction(neighbors_list, rgb, incoming_rgb, sender_id_string, prev_senders, "topleft")
        forward_strip_to_neighbors_direction(neighbors_list, rgb, incoming_rgb, sender_id_string, prev_senders, "bottomleft")
    elif (direction == "y-axis-up"):
        print("y up")
        handle_strip_self("stripSelf X X rgb:" + incoming_rgb)
        LEDStripColor = incoming_rgb

    elif (direction == "y-axis-down"):
        print("y down")
        handle_strip_self("stripSelf X X rgb:" + incoming_rgb)
        LEDStripColor = incoming_rgb

    return

def handle_LED_self(data):
    global LEDColor

    message_type, sender_id_string, prev_senders, incoming_msg_id, content = parse_message(data)
    incoming_color = content["color"]

    if LEDColor == incoming_color:
        redLED.off()
        greenLED.off()
        blueLED.off()
        return

    redLED.off()
    greenLED.off()
    blueLED.off()
    pyb.LED(int(incoming_color)).on()

    LEDColor = incoming_color

    return


# for keeping track of last orientation in IMU mode
prev_orientation = "none"

def handle_paint(data):
    global current_paint
    global paint_palette
    global iteration
    global LEDStripColor
    global prev_orientation
    global curr_msg_id


    message_type, sender_id_string, prev_senders, incoming_msg_id, content = parse_message(data)

    direction = content["direction"]

    if (direction == "x-axis-up"):
        print("x up")
        prev_orientation = "x-axis-up"
        return

    elif (direction == "y-axis-down"):
        print("y axis")
        prev_orientation = "y-axis-down"
        return

    elif (direction == "y-axis-up"):
        print("y up")

        if prev_orientation == "y-axis-up":
            return

        prev_orientation = "y-axis-up"
        selected_color = paint_palette[iteration]
        print(selected_color, LEDStripColor)

        handle_strip_paint("stripSelf X X rgb:" + selected_color)
        time.sleep(1.25)
        handle_strip_self("stripSelf X X rgb:" + LEDStripColor)

        current_paint = selected_color

        iteration += 1

        if iteration == len(paint_palette):
            iteration = 0

    elif (direction == "z-axis-up"):
        if prev_orientation == "z-axis-up":
            return

        if LEDStripColor == "(0,0,0)":
            print("hi")
            handle_bloom_self("selfBloom X X bloom:unbloom")

        prev_orientation = "z-axis-up"
        return

    elif (direction == "z-axis-down"):
        print("z-down")
        prev_orientation = "z-axis-down"
        return


########################### IDLE MESSAGE LISTENING ##########################


def idle_listening(s):
    global neighbors_list
    global LEDColor
    global mode
    global last_command_time
    global listeningOn
    global curr_msg_id


    #lets us know we've entered new mode
    handle_strip_self("stripSelf x x rgb:(100,100,100)")
    time.sleep(2)

    while True:
        evts = poller.poll(10)

        ##################### MESSAGE + STATE MANAGEMENT ######################
        if listeningOn:
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
                        elif "bloomSelf" in data:
                            handle_bloom_self(data)
                        elif "stripSelf" in data:
                            handle_strip_self(data)
                        elif "LEDSelf" in data:
                            handle_LED_self(data)


########## WEARABLE MODE #############

def wearable(s):
    global neighbors_list
    global LEDColor
    global mode
    global last_command_time
    global listeningOn
    global curr_msg_id

    #lets us know we've entered new mode
    handle_strip_self("stripSelf x x rgb:(100,100,100)")
    time.sleep(2)

    while True:
        evts = poller.poll(10)

        ##################### MESSAGE + STATE MANAGEMENT ######################
        if listeningOn:
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
                        elif "bloomSelf" in data:
                            handle_bloom_self(data)
                        elif "stripSelf" in data:
                            handle_strip_self(data)
                        elif "LEDSelf" in data:
                            handle_LED_self(data)
                        elif "wearablePulse" in data:
                            handle_pulse(data)
                        elif "wearableExpand" in data:
                            handle_expand(data)
                        elif "wearableIMU" in data:
                            handle_imu(data)


########## PROXIMITY COLOR MODE #############

def proximity_color(s):
    global neighbors_list
    global LEDColor
    global mode
    global last_command_time
    global listeningOn
    global sheetColor
    global curr_msg_id


    # select random interaction result: bloom, unbloom, LED
    selection = random.randint(1, 18)

    # Variables for moving average
    window_size = 100  # You can adjust the window size as needed
    proximity_values = []

    # Function to calculate moving average
    def moving_average(values):
        if len(values) < window_size:
           return sum(values) / len(values)
        else:
           return sum(values[-window_size:]) / window_size

    #lets us know we've entered new mode
    #lets us know we've entered new mode
    handle_strip_self("stripSelf x x rgb:(100,100,100)")
    time.sleep(2)

    allow_LED_update = True
    sent = False

    while True:

        # LED Coloring Mode (1/9 chance)
        if selection <= 2:
            proximity = tof.read()
            proximity_values.append(proximity)
            proximity_avg = moving_average(proximity_values)
            if proximity < 700:
                if sheetColor == "orange":
                    handle_strip_self("stripSelf x x rgb:(150,40,0)")
                    curr_msg_id = generate_random_id(6)
                    LEDStripColor = '(150,40,0)'
                    forward_strip_to_neighbors(neighbors_list, LEDStripColor, 'x', ['x'])
                elif sheetColor == "yellow":
                    handle_strip_self("stripSelf x x rgb:(150,105,0)")
                    curr_msg_id = generate_random_id(6)
                    LEDStripColor = '(150,105,0)'
                    forward_strip_to_neighbors(neighbors_list, LEDStripColor, 'x', ['x'])
                elif sheetColor == "red":
                    handle_strip_self("stripSelf x x rgb:(150,3,0)")
                    curr_msg_id = generate_random_id(6)
                    LEDStripColor = '(150,3,0)'
                    forward_strip_to_neighbors(neighbors_list, LEDStripColor, 'x', ['x'])

            else:
                handle_strip_self("stripSelf x x rgb:(0,0,0)")
                curr_msg_id = generate_random_id(6)
                LEDStripColor = '(0,0,0)'
                forward_strip_to_neighbors(neighbors_list, LEDStripColor, 'x', ['x'])

        # Bloom Mode (1/18 chance)
        elif selection == 3 or selection == 4:
            proximity = tof.read()
            allow_LED_update = True

            if proximity < 200:
                curr_msg_id = generate_random_id(6)
                handle_bloom_update("bloomUpdate x x bloom:bloom")

        # Unbloom Mode (1/18)
        elif selection == 5 or selection == 6:
            proximity = tof.read()
            allow_LED_update = True

            if proximity < 200:
                curr_msg_id = generate_random_id(6)
                handle_bloom_update("bloomUpdate x x bloom:unbloom")

        # Remove oldest value if window size exceeded
        if len(proximity_values) > window_size:
            proximity_values.pop(0)

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
                    elif "bloomSelf" in data:
                        handle_bloom_self(data)
                    elif "stripSelf" in data:
                        handle_strip_self(data)
                    elif "LEDSelf" in data:
                        handle_LED_self(data)


########## PROXIMITY TRANSIENT COLOR MODE #############

def proximity_transient_color(s):
    global neighbors_list
    global LEDColor
    global mode
    global last_command_time
    global listeningOn
    global sheetColor
    global curr_msg_id

    handle_strip_self("stripSelf x x rgb:(0,0,0)")
    time.sleep(2)

    while True:
        proximity = tof.read()
        if proximity < 800:
            if sheetColor == "orange":
                handle_strip_self("stripSelf x x rgb:(150,40,0)")
                LEDStripColor = '(150,40,0)'
            elif sheetColor == "yellow":
                handle_strip_self("stripSelf x x rgb:(150,105,0)")
                LEDStripColor = '(150,105,0)'
            elif sheetColor == "red":
                handle_strip_self("stripSelf x x rgb:(150,3,0)")
                LEDStripColor = '(150,3,0)'
        else:
            handle_strip_self("stripSelf x x rgb:(0,0,0)")
            LEDStripColor = '(0,0,0)'

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
                    elif "stripUpdate" in data and allow_LED_update:
                        handle_strip_update(data)
                    elif "stripDirectionUpdate" in data and allow_LED_update:
                        handle_strip_direction_update(data)
                    elif "bloomSelf" in data:
                        handle_bloom_self(data)
                    elif "stripSelf" in data:
                        handle_strip_self(data)
                    elif "LEDSelf" in data:
                        handle_LED_self(data)


########## PROXIMITY BLOOM MODE #############

def proximity_bloom(s):
    global neighbors_list
    global LEDColor
    global mode
    global last_command_time
    global listeningOn
    global sheetColor
    global curr_msg_id
    global step_sleep
    global bloom_thresh
    global unbloom_thresh

    # select random interaction result: bloom, unbloom, LED

    #lets us know we've entered new mode
    if sheetColor == "orange":
        handle_strip_self("stripSelf x x rgb:(150,40,0)")
        LEDStripColor = '(150,40,0)'
    elif sheetColor == "yellow":
        handle_strip_self("stripSelf x x rgb:(150,105,0)")
        LEDStripColor = '(150,105,0)'
    elif sheetColor == "red":
        handle_strip_self("stripSelf x x rgb:(150,3,0)")
        LEDStripColor = '(150,3,0)'
    time.sleep(2)

    init = tof2.read()

    hit_thresh = False
    while True:
        proximity = tof.read()
        dist_from_stop = tof2.read()

        if proximity < 150:

            if hit_thresh:
                # flatten (upwards)

                dist_from_stop = tof2.read()
                if dist_from_stop > unbloom_thresh:
                    hit_thresh = False

                for i in range(150):
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

                    time.sleep(step_sleep)


            else:
                dist_from_stop = tof2.read()
                if dist_from_stop < bloom_thresh:
                    hit_thresh = True
                # bloom (downwards)
                for i in range(150):

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

                    time.sleep(step_sleep)



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
                    elif "stripUpdate" in data and allow_LED_update:
                        handle_strip_update(data)
                    elif "stripDirectionUpdate" in data and allow_LED_update:
                        handle_strip_direction_update(data)
                    elif "bloomSelf" in data:
                        handle_bloom_self(data)
                    elif "stripSelf" in data:
                        handle_strip_self(data)
                    elif "LEDSelf" in data:
                        handle_LED_self(data)

########## GAME MODE #############

#def game(s):
#    global neighbors_list
#    global LEDColor
#    global mode
#    global last_command_time
#    global listeningOn
#    global sheetColor

#    # select random interaction result: bloom, unbloom, LED

#    #lets us know we've entered new mode
#    handle_strip_self("stripSelf x x rgb:(100,100,100)")
#    time.sleep(2)

#    ## ADD BLOOM AT BEGINNING OF THIS MODE FOR VISIBLE LED
#    pointEnd = False
#    while True:

#        ## beginning of round
#        ## countdown pulse 3, 2, 1
#        proximity = tof.read()

#        # you need 20 consecutive hits to win
#        for _ in range(20):
#            # randomly choose a module to be target with 1/36 chance per round
#            selection = random.randint(0, 35)

#            if selection == 1:
#                handle_module_action("stripSelf x x rgb:(100,0,0)")  # Set the module to red

#                time_elapsed = time.time()

#                while True:
#                    # Get proximity information (you need to define how to get this)
#                    proximity = get_proximity()  # Assuming you have a function to get proximity

#                    if proximity <= 100:
#                        handle_module_action("stripSelf x x rgb:(100,100,100)")  # Set the module to white
#                        break

#                    if time.time() - time_elapsed >= 10:
#                        # End the game if the player doesn't hit the module within 10 seconds
#                        send_to_all_ports("Game Over", range(50000, 50036))
#                        break

#                    # You may want to add some delay here to avoid continuous checking
#                    time.sleep(0.1)  # Adjust the delay as needed

#        evts = poller.poll(10)

#        ##################### MESSAGE + STATE MANAGEMENT ######################
#        for sock, evt in evts:
#            if evt and select.POLLIN:
#                if sock == s:
#                    data, addr = s.recvfrom(1024)
#                    data = data.decode()

#                    last_command_time = time.time()

#                    if "neighborsUpdate" in data:
#                        handle_neighbors_update(data)
#                    elif "modeUpdate" in data:
#                        handle_mode_update(data)
#                        return
#                    elif "LEDColorUpdate" in data:
#                        handle_LED_color_update(data)
#                    elif "LEDColorDirectionUpdate" in data:
#                        handle_LED_color_direction_update(data)
#                    elif "bloomUpdate" in data:
#                        handle_bloom_update(data)
#                    elif "stripUpdate" in data and allow_LED_update:
#                        handle_strip_update(data)
#                    elif "stripDirectionUpdate" in data and allow_LED_update:
#                        handle_strip_direction_update(data)
#                    elif "bloomSelf" in data:
#                        handle_bloom_self(data)
#                    elif "stripSelf" in data:
#                        handle_strip_self(data)
#                    elif "LEDSelf" in data:
#                        handle_LED_self(data)

######### LIGHT PAINTING MODE #########
def light_painting(s):
    global neighbors_list
    global LEDColor
    global mode
    global last_command_time
    global listeningOn
    global sheetColor
    global current_paint
    global paint_palette
    global iteration

    #lets us know we've entered new mode
    handle_strip_self("stripSelf x x rgb:(0,0,0)")
    time.sleep(2)

    handle_bloom_self("bloomSelf x x bloom:bloom")
    touched = False
    while True:

        proximity = tof.read()

        if proximity < 50 and not touched:
            print(touched)
            handle_strip_self("stripSelf x x rgb:" + current_paint)
            LEDStripColor = current_paint
            touched = True
#            time.sleep(0.5)

        elif proximity < 50 and LEDStripColor != current_paint and not touched:
            handle_strip_self("stripSelf x x rgb:" + current_paint)
            LEDStripColor = current_paint
            touched = True
#            time.sleep(0.5)

        elif proximity < 50 and touched:
            print(touched)
            handle_strip_self("stripSelf x x rgb:(0,0,0)")
            LEDStripColor = '(0,0,0)'
            touched = False
#            time.sleep(0.5)

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
                    elif "stripUpdate" in data and allow_LED_update:
                        handle_strip_update(data)
                    elif "stripDirectionUpdate" in data and allow_LED_update:
                        handle_strip_direction_update(data)
                    elif "bloomSelf" in data:
                        handle_bloom_self(data)
                    elif "stripSelf" in data:
                        handle_strip_self(data)
                    elif "LEDSelf" in data:
                        handle_LED_self(data)
                    elif "wearablePaint" in data:
                        handle_paint(data)


##################@### WEBSERVER SOCKET + STREAMING / LISTENING ################

WEBPORT = 65000 + module_ID

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
    global LEDStripColor

    #lets us know we've entered new mode
    handle_strip_self("stripSelf x x rgb:(100,100,100)")
    time.sleep(2)

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

        evts = poller.poll(0)

        ##################### MESSAGE + STATE MANAGEMENT ######################
        for sock, evt in evts:
            if evt and select.POLLIN:
                if sock == s:
                    data, addr = s.recvfrom(1024)
                    data = data.decode()
                    print(data)
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

###############################################################################

while(True):

#    print(tof2.read())
    ##################### MODE MANAGEMENT ######################
    if mode == "mpegPose":
        try:
           MPEG_streaming(s, webserver)
        except:
            print("Reconnect Camera")
    elif mode == "wearable":
        wearable(s)
    elif mode == "proximityColor":
        proximity_color(s)
    elif mode == "proximityBloom":
        proximity_bloom(s)
    elif mode == "lightPainting":
        light_painting(s)
    elif mode == "proximityTransient":
        proximity_transient_color(s)
    else:
        idle_listening(s)
