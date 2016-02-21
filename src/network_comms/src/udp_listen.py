import socket

UDP_IP = "192.168.43.218"#"192.168.43.12" #"127.0.0.1" 
UDP_PORT = 21234

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Internet, UDP
sock.bind((UDP_IP, UDP_PORT))

while True:
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    print "received message:", data
