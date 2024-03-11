# NICLA ID NEIGHBORS - By: jadbendarkawi - Mon Feb 12 2024

import sensor, image, time, network, socket, pyb
from socket import *
import select
from vl53l1x import VL53L1X
from machine import I2C
import tf
import math



clock = time.clock()


########################## MODULE VARIABLES ###############################

# must match the id of the attached April Tag
module_ID = 2

# list of tuples where neighbor[0] = location, neighbor[1] = id ex. (topright, 4)
# updates on neighborsUpdate messages
neighbors_list = []

# current mode
mode = "mpegPose"

# on board LED color
LEDcolor = ""

# background LED strip color
LEDStripColor = ""

# we will append this to the ifconfig to route camera streams properly
webhost_unique = str(200 + module_ID)

# used for checking when the last command was recieved
last_command_time = time.time()

##########################################################################


######################### SENSORS + BOARD STUFF #########################

redLED = pyb.LED(1) # built-in red LED
greenLED = pyb.LED(2) # built-in green LED
blueLED = pyb.LED(3) # built-in blue LED

tof = VL53L1X(I2C(2)) # distance sensor

sensor.reset()  # Reset and initialize the sensor.
sensor.set_pixformat(sensor.RGB565)  # Set pixel format to RGB565 (or GRAYSCALE)
sensor.set_framesize(sensor.QVGA)  # Set frame size to QVGA (320x240)
sensor.set_windowing((240, 240))  # Set 240x240 window.
sensor.skip_frames(time=2000)  # Let the camera adjust.

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

###############################################################################



################## SETTING UP WIFI NETWORK + SOCKET BROADCAST #################

SSID='BlueSwarm' # Network SSID
KEY='Tpossr236'  # Network key

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, KEY)
while not wlan.isconnected():
    print("Trying to connect. Note this may take a while...")
    time.sleep_ms(1000)


HOST ='192.168.0.' + webhost_unique  # we will have a standard for this

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

def return_to_base_conditions():
    # Implement your logic to return to base conditions
    print("Returning to base conditions...")

################# FORWARDING FUNCTIONS + MESSAGE PARSER ########################

# takes in list of neighbors and color to propogate to neighbors
def forward_LED_color_to_neighbors(neighbors, color, prevSender):

    redLED.off()
    greenLED.off()
    blueLED.off()
    pyb.LED(int(color)).on()

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

    redLED.off()
    greenLED.off()
    blueLED.off()
    pyb.LED(int(color)).on()

    # for each neighbor, forward color message to their module_ID PORT
    for neighbor in neighbors:
        if neighbor[1] is not prevSender and neighbor[0] is direction:
            sendData = "LEDColorDirectionUpdate" + " " + str(module_ID) + " " + "color:" + color + " " + "direction:" + direction
            try:
                print(neighbor)
                s.sendto(sendData.encode(), ('255.255.255.255', 50000 + int(neighbor[1])))
            except OSError as e:
                print("Error sending UDP message:", e)


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

#############################################################################



##################@### WEBSERVER SOCKET + STREAMING / LISTENING ################

WEBPORT = 8080 + module_ID  # we will have a standard for this

# Create server socket
webserver = socket(AF_INET, SOCK_STREAM)
webserver.setsockopt(SOL_SOCKET, SO_REUSEADDR, True)

# Bind and listen
webserver.bind([HOST, WEBPORT])
webserver.listen(5)

# Set server socket to blocking
webserver.setblocking(True)

###############################################################################



########################### IDLE MESSAGE LISTENING ##########################

def idle_listening(s):
    global neighbors_list
    global LEDColor
    global module_ID
    global mode

    while True:
        evts = poller.poll(10)

        ##################### MESSAGE + STATE MANAGEMENT ######################
        for sock, evt in evts:
            if evt and select.POLLIN:
                if sock == s:
                    data, addr = s.recvfrom(1024)
                    data = data.decode()


                    if "neighborsUpdate" in data:

                        message_type, sender_id, content = parse_message(data)

                        neighbors_list = list(content.items())

                        print("neighbors updated to: " + str(neighbors_list))

                    elif "modeUpdate" in data:

                        if "mpegPose" in data:
                            mode = "mpegPose"
                            return
                        elif "faceDetection" in data:
                            mode = "faceDetection"
                            return
                        else:
                            mode = "idle"
                            return

                    elif "LEDColorUpdate" in data:
                        print("color update")
                        message_type, sender_id, content = parse_message(data)

                        incoming_color = content["color"]

                        LEDColor = incoming_color

                        forward_LED_color_to_neighbors(neighbors_list, incoming_color, sender_id)

                    elif "LEDColorDirectionUpdate" in data:
                        print("color direction update")
                        message_type, sender_id, content = parse_message(data)

                        incoming_color = content["color"]
                        direction = content["direction"]

                        LEDColor = incoming_color

                        forward_LED_color_to_neighbors_direction(neighbors_list, incoming_color, sender_id, direction)

#############################################################################



#################### MPEG STREAMING TO WEBSERVER ##############################

def MPEG_streaming(s, webserver):
    global neighbors_list
    global LEDColor
    global module_ID
    global mode

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

    # FPS clock
    clock = time.clock()

    # Start streaming images
    # NOTE: Disable IDE preview to increase streaming FPS.
    while True:

        clock.tick()  # Track elapsed milliseconds between snapshots().
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

                    if "neighborsUpdate" in data:

                        message_type, sender_id, content = parse_message(data)

                        neighbors_list = list(content.items())

                        print("neighbors updated to: " + str(neighbors_list))

                    elif "modeUpdate" in data:

                        if "mpegPose" in data:
                            mode = "mpegPose"
                            return
                        elif "faceDetection" in data:
                            mode = "faceDetection"
                            return
                        else:
                            mode = "idle"
                            return

                    elif "LEDColorUpdate" in data:
                        print("color update")
                        message_type, sender_id, content = parse_message(data)

                        incoming_color = content["color"]

                        LEDColor = incoming_color

                        forward_LED_color_to_neighbors(neighbors_list, incoming_color, sender_id)

                    elif "LEDColorDirectionUpdate" in data:
                        print("color direction update")
                        message_type, sender_id, content = parse_message(data)

                        incoming_color = content["color"]
                        direction = content["direction"]

                        LEDColor = incoming_color

                        forward_LED_color_to_neighbors_direction(neighbors_list, incoming_color, sender_id, direction)


###############################################################################



#################### FACE DETECTION W/ PROXIMITY ##############################

def face_detection(s):
    global neighbors_list
    global LEDColor
    global module_ID
    global mode

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
                    continue  # no detections for this class?

                greenLED.on()


                for d in detection_list:
                    [x, y, w, h] = d.rect()
                    center_x = math.floor(x + (w / 2))
                    center_y = math.floor(y + (h / 2))
                    img.draw_circle((center_x, center_y, 12), color=colors[i], thickness=2)


        else:
            blueLED.on()
            redLED.off()
            greenLED.off()

        evts = poller.poll(10)

        ##################### MESSAGE + STATE MANAGEMENT ######################
        for sock, evt in evts:
            if evt and select.POLLIN:
                if sock == s:
                    data, addr = s.recvfrom(1024)
                    data = data.decode()

                    last_command_time = time.time()

                    if "neighborsUpdate" in data:

                        message_type, sender_id, content = parse_message(data)

                        neighbors_list = list(content.items())

                        print("neighbors updated to: " + str(neighbors_list))

                    elif "modeUpdate" in data:

                        if "mpegPose" in data:
                            mode = "mpegPose"
                            return
                        elif "faceDetection" in data:
                            mode = "faceDetection"
                            return
                        else:
                            mode = "idle"
                            return

                    elif "LEDColorUpdate" in data:
                        print("color update")
                        message_type, sender_id, content = parse_message(data)

                        incoming_color = content["color"]

                        LEDColor = incoming_color

                        forward_LED_color_to_neighbors(neighbors_list, incoming_color, sender_id)

                    elif "LEDColorDirectionUpdate" in data:
                        print("color direction update")
                        message_type, sender_id, content = parse_message(data)

                        incoming_color = content["color"]
                        direction = content["direction"]

                        LEDColor = incoming_color

                        forward_LED_color_to_neighbors_direction(neighbors_list, incoming_color, sender_id, direction)

        # Check if X seconds have passed since the last command
        if time.time() - last_command_time >= 3:
            return_to_base_conditions()


########## MAIN LOOP ##########

while(True):

    ##################### MODE MANAGEMENT ######################

    if mode == "mpegPose":
        try:
           MPEG_streaming(s, webserver)
        except:
            print("Reconnect Camera")
    elif mode == "faceDetection":
        face_detection(s)
    else:
        idle_listening(s)

    ############################################################

    print(mode)
