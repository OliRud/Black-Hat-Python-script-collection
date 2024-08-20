#a UDP client can be made similarly to A tcp but with slight changes

#UDP is a connectionless protocol

import socket

target_host = "127.0.0.1"
target_port = 9997

client = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) #DGRAM is the new socket type

client.sendto(b"AAABBBCCC",(target_host,target_port))

data,addr = client.recvfrom(4096)

print(data.decode())
client.close()