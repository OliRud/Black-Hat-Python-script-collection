import socket 

target_host = "0.0.0.0" #IP and pot set to connect to the TCP server in script 3
target_port = 9998

#create socket object
client =  socket.socket(socket.AF_INET, socket.SOCK_STREAM) #AF_NET indicates we're using IPv4 address and SOCK_STREAM to create a TCP client

#connect the client
client.connect((target_host,target_port))

#send data
client.send(b"Hello")

#recieve data
response = client.recv(4096)

print("\nRESPONSE\n"+response.decode())
client.close()

#this code makes the assumption that:
#The connection will always go through
#The server expects us to send data first
#the server will always respond in a timely fashion