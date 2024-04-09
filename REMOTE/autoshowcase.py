import socket
import time
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
# Enable broadcasting mode
server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
server.bind(("", 20000))
import random

# Each row is a column from bottom to top i.e grid[0][0] is the bottom left most module
grid = [
    [5,13,27],
    [4,14,28],
    [1,23,2],
    [34,29,10],
    [32,22,15],
    [35,8,25],
    [9,16,19],
    [31,20,11],
    [17,33,12],
    [0,30,7],
    [6,3,21],
    [24,18,26]
]

### UNBLOOM ALL TO FLAT ####
for column in grid:
    for item in column:
        for _ in range(3):
            bloom = "bloomSelf X bloom:unbloom"
            server.sendto(bloom.encode(), ('255.255.255.255', 50000 + item))
            strip = "stripSelf X rgb:(0,0,0)"
            server.sendto(strip.encode(), ('255.255.255.255', 50000 + item))

time.sleep(30)

while True:
    #### LEFT TO RIGHT BLOOM + ORANGE LED ####
    for column in grid:
        for item in column:
            for _ in range(3):
                strip = "stripSelf X rgb:(150,60,0)"
                server.sendto(strip.encode(), ('255.255.255.255', 50000 + item))
                time.sleep(0.5)
                bloom = "bloomSelf X bloom:bloom"
                server.sendto(bloom.encode(), ('255.255.255.255', 50000 + item))
                time.sleep(0.5)
        time.sleep(0.5)

    time.sleep(20)

    #### RIGHT TO LEFT UNBLOOM + BLUE LED ####
    for column in reversed(grid):
        for item in reversed(column):
            for _ in range(3):
                strip = "stripSelf X rgb:(0,100,100)"
                server.sendto(strip.encode(), ('255.255.255.255', 50000 + item))
                time.sleep(0.5)
                bloom = "bloomSelf X bloom:unbloom"
                server.sendto(bloom.encode(), ('255.255.255.255', 50000 + item))
                time.sleep(0.5)
        time.sleep(0.5)

    time.sleep(15)

    #### BOTTOM TO TOP ROW BLOOM + PURPLE LED ####
    for i in range(len(grid[0])):
        for column in grid:
            item = column[i]
            strip = "stripSelf X rgb:(50,100,0)"
            bloom = "bloomSelf X bloom:bloom"
            server.sendto(strip.encode(), ('255.255.255.255', 50000 + item))
            server.sendto(bloom.encode(), ('255.255.255.255', 50000 + item))
            time.sleep(0.5)

        time.sleep(4)

    time.sleep(15)

    #### RANDOM LED'S UNTIL ALL ONE COLOR THEN RANDOM BLOOMS ####

    all_items = [item for column in grid for item in column]
    random.shuffle(all_items)  # Shuffle the items randomly

    # Send the message randomly to each item until all items have been visited
    while all_items:
        item = all_items.pop()  # Take an item from the shuffled list
        strip = "stripSelf X rgb:(100,0,100)"
        server.sendto(strip.encode(), ('255.255.255.255', 50000 + item))
        time.sleep(2)

    time.sleep(10)

    all_items = [item for column in grid for item in column]
    random.shuffle(all_items)  # Shuffle the items randomly

    while all_items:
        item = all_items.pop()  # Take an item from the shuffled list
        bloom = "bloomSelf X bloom:unbloom"
        server.sendto(bloom.encode(), ('255.255.255.255', 50000 + item))
        time.sleep(5)

    time.sleep(15)

