import socket
import time
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
# Enable broadcasting mode
server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
server.bind(("", 20000))

'''
3    11   13

8    6    10

2    7    5

'''
grid = [
    [24, 17, 9],
    [2, 10, 11],
    [31, 0, 4]
]


for column in grid:
    for item in column:
        for _ in range(3):
            bloom = "bloomSelf X bloom:unbloom"
            server.sendto(bloom.encode(), ('255.255.255.255', 50000 + item))
            strip = "stripSelf X rgb:(0,0,0)"
            server.sendto(strip.encode(), ('255.255.255.255', 50000 + item))

time.sleep(20)

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

time.sleep(3)

# UNDER HERE
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



