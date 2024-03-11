import sensor
import time
import math
import pyb
import socket
import network

SSID = 'BlueSwarm'  # Network SSID
KEY = 'Tpossr236'  # Network key

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, KEY)
while not wlan.isconnected():
    print("Trying to connect. Note this may take a while...")
    time.sleep_ms(1000)

# handling socket module usage for MCU
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.setsockopt(socket.SOL_SOCKET, 0x20, 1)
# Enable broadcasting mode
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.setsockopt(socket.SOL_SOCKET, 0x20, 1)
server.bind(("", 30001))

pyb.LED(3).on()  # visual for wifi connection

sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(time=2000)
sensor.set_auto_gain(False)
sensor.set_auto_whitebal(False)
clock = time.clock()

f_x = (2.8 / 3.984) * 160
f_y = (2.8 / 2.952) * 120
c_x = 160 * 0.5
c_y = 120 * 0.5

def calculate_distance(tag1, tag2):
    return math.sqrt((tag1.cx() - tag2.cx())**2 + (tag1.cy() - tag2.cy())**2)

def calculate_neighbors(tag, tags, num_neighbors):
    neighbors = []

    # Sort tags based on distance to the current tag
    sorted_tags = sorted(tags, key=lambda x: calculate_distance(tag, x))

    # Collect the nearest neighbors
    for other_tag in sorted_tags[:num_neighbors]:
        if tag != other_tag:
            neighbors.append(other_tag)

    return neighbors

def degrees(radians):
    return (180 * radians) / math.pi

def relative_position(tagCX,tagCY, neighborCX, neighborCY):
    dx = tagCX - neighborCX
    dy = tagCY - neighborCY

    proximity_y_threshold = 10  # Adjust this threshold based on your needs

    if abs(dx) > 75 or abs(dy) > 75:
        return "far"
    elif abs(dx) < proximity_y_threshold and dy > 0:
        return 'top'
    elif abs(dx) < proximity_y_threshold and dy < 0:
        return 'bottom'
    elif dx < 0 and abs(dy) < proximity_y_threshold:
        return 'right'
    elif dx > 0 and abs(dy) < proximity_y_threshold:
        return 'left'
    elif dx < 0 and dy > 0:
        return 'topright'
    elif dx < 0 and dy < 0:
        return 'bottomright'
    elif dx > 0 and dy > 0:
        return 'topleft'
    elif dx > 0 and dy < 0:
        return 'bottomleft'
    else:
        return 'unknown'

def neighbors_string(tagCX,tagCY, neighbors):
    res = ""
    for neighbor in neighbors:
        location = relative_position(tagCX,tagCY,neighbor.cx(), neighbor.cy())
        res += f"{location}:{neighbor.id()} "
    return res

while True:
    clock.tick()
    img = sensor.snapshot()

    detected_modules = img.find_apriltags(fx=f_x, fy=f_y, cx=c_x, cy=c_y)

    for tag in detected_modules:

        img.draw_rectangle(tag.rect(), color=(255, 0, 0))
        img.draw_cross(tag.cx(), tag.cy(), color=(0, 255, 0))

        neighbors = calculate_neighbors(tag, detected_modules, num_neighbors=9)

        print_args = (
            tag.id(),
            tag.x_translation(),
            tag.y_translation(),
            tag.z_translation(),
            neighbors
        )

        sendData = f"neighborsUpdate {print_args[0]} {neighbors_string(tag.cx(), tag.cy(), print_args[4])}"

        print(sendData)

        server.sendto(sendData.encode(), ('255.255.255.255', 50000 + print_args[0]))
