import socket
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
# Enable broadcasting mode
server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
server.bind(("", 20000))

for i in range(36):
        for _ in range(3):
            sendData = "modeUpdate wearable"
            server.sendto(sendData.encode(), ('255.255.255.255', 50000 + i))

# while True:

#     sendData = input()
#     for _ in range(3):
#         server.sendto(sendData.encode(), ('255.255.255.255', 50000))


