#When running penetration tests in an enterprise enviroment, you most likely won't have wireshark available. So we have to make our own!

#objectives: Display communication between the local and remove machine to the console.
#          ->receive data from an incoming socket from either the local or remote machine.
#          ->manage the traffic direction between the 2 machines.
#          ->set up listening socket and pass to a handler.

import sys
import socket
import threading

HEX_FILTER = ''.join(
    [(len(repr(chr(i))) == 3) and chr(i) or '.' for i in range(256)])

def hexdump(src, length = 16, show = True): #length is the ammount of characters per line

    #decoding the byte string
    if isinstance(src,bytes):
        src = src.decode

    results = list()
        
    for i in range(0,len(src),length):
            
        #grab a piece of the string to store as a variable
        word = str(src[i:i+length])
            
        #translate built in function is used to translate the string into the variable printable.
        printable = word.translate(HEX_FILTER)
            
        hexa = ''.join([f'{ord(c):02x}' for c in word])
            
        hexwidth = length*3

        results.append(f'{i:04x} {hexa:<{hexwidth}} {printable}')
            
        
    if show:
            
        for line in results:
            print(line)
        
    else:
        return results


#function to recieve data
def receive_from(connection):

    #create empty buffer
    buffer = b""
    connection.settimeout(5)

    try:
        while True:
            data = connection.revr(4086)
            if not data:
                break
            buffer += data
    except:
        pass
    
    return buffer


def request_handler(buffer):
    return buffer

def response_handler(buffer):
    return buffer


def proxy_handler(client_socket, remote_host, remote_port, receive_first):

    #connect to remote host
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))

    #check to make sure we dont ned t ofirst initiate a connection and request data before entering the main loop
    if receive_first:
        remote_buffer = receive_from(remote_socket) #accepts a connection socket object and performs a recieve
        hexdump(remote_buffer)

    remote_buffer = response_handler(remote_buffer) #then we pass the output to the response_handler function
    if len(remote_buffer):
        print("[==>] received %d bytes from localhost." % len(remote_buffer))
        client_socket.send(remote_buffer)

    #set up loop to read from local client, process the data, send it to remote, red the remote client, process data, send it to the local client until no more data is left.
    while True:
        local_buffer = receive_first (client_socket)
        if len(local_buffer):
            line = "[-->]Recieved %d bytes from remote." % len(remote_buffer)
            print(line)
            hexdump(local_buffer)

            local_buffer = request_handler(local_buffer)
            remote_socket.send(local_buffer)
            print("[==>] Sent to remote.")

        remote_buffer = receive_from(remote_socket)
        if len(remote_buffer):
            print("[<==] Received %d bytes from remote." % len(remote_buffer))
            hexdump(remote_buffer)

            remote_buffer = response_handler(remote_buffer)
            client_socket.send(remote_buffer)
            print("[<==] sent to localhost.")
        
        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print("[*] No more data. Closing connections.")
            break


def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #first we bind the socket
    try:
        server.bind((local_host, local_port)) 
    except Exception as e:
        print("problem on bind: %r" % e)
        print("[||] failed to listen on %s:%d" % (local_host, local_port))
        print("[||] check for other listening sockets or corrent permissions.")
        sys.exit(0)
    
    print("[*] Listening on %s:%d" % (local_host, local_port)) #then we listen
    server.listen(5)

    while True: #the loop we wait for a request and then pass it onto the proxy handler
        client_socket, addr = server.accept()
        #print local connection information
        line = "> Received incoming connection from %s:%d" % (addr[0], addr[1])
        print(line)
        #start a thread to speak to the remote host
        proxy_thread = threading.Thread(
            target=proxy_handler,
            args=(client_socket, remote_host,
            remote_port, receive_first))
        proxy_thread.start()



#main
if len(sys.argv[1:]) != 5: #checks if 5 arguments are passed

    print("Usage: ./proxy.py [localhost] [localport]", end='')
    print("[remote_host] [remote_port] [receive_first]")
    print("Example: ./proxy.py 127.0.0.1 9000 10.12.123.1 900 True")
    sys.exit(0)
local_host = sys.argv[1]
local_port = int(sys.argv[2])

remote_host = sys.argv[3]
remote_port = int(sys.argv[4])

receive_first = sys.argv[5]

if "True" in receive_first:
    receive_first = True
else:
    receive_first = False

server_loop(local_host, local_port, remote_host, remote_port, receive_first)