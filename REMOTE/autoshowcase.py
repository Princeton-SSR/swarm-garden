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
    [3, 8, 2],
    [11, 6, 7],
    [13, 10, 5]
]

for column in grid:
    for item in column:
        for _ in range(3):
            sendData = "bloomSelf X bloom:bloom"
            server.sendto(sendData.encode(), ('255.255.255.255', 50000 + item))
            time.sleep(0.75)
    time.sleep(0.25)

for column in grid:
    for item in column:
        for _ in range(3):
            sendData = "stripSelf X rgb:(100,0,100)"
            server.sendto(sendData.encode(), ('255.255.255.255', 50000 + item))
            time.sleep(0.75)
    time.sleep(0.25)