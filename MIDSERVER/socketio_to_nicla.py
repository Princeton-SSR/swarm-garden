import socket
import socketio


# handling socket module usage for MCU
server = socket.socket(socket.AF_INET,
                       socket.SOCK_DGRAM,
                         socket.IPPROTO_UDP)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
# Enable broadcasting mode
server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
server.bind(("", 65535))


sio = socketio.Client()

@sio.on('message')
def on_message(data):
    message = data[1:]
    print('Forwarding message to Nicla:', message)

    module_port = 50000 + int(data[0])
    
    server.sendto(message.encode(), ('255.255.255.255', module_port))
    return 0

@sio.on('connect')
def on_connect():
    print('Connected to server')

@sio.on('disconnect')
def on_disconnect():
    print('Disconnected from server')

sio.connect('http://localhost:6147')

# Keep the program running to continue receiving messages
# while True:
#     data = input("type here: ")
#     server.sendto(data.encode(), ('255.255.255.255', 50000))

try:
    sio.wait()
   

except KeyboardInterrupt:
    sio.disconnect()
