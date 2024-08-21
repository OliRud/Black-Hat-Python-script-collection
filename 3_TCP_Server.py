import socket
import threading

IP = '0.0.0.0'
PORT = 9998

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((IP,PORT)) #set the port and ip for the server to listen on
    server.listen(5) #set the maximum number of connections
    print(f"[*] Listening on {IP}:{PORT}")
    
    while True:
        client,address = server.accept() #the loop runs until a connection has been established
        print(f"[*] Accepted Connection from {address[0]}:{address[1]}") #
        client_handler = threading.Thread(target=handle_client,args=(client,))
        client_handler.start() # we lead the script to our handle_client function so it can accept another connection
       
def handle_client(client_socket): #this function sends a message back to the client
    with client_socket as sock:
        request = sock.recv(1024)
        print(f'[*] Recived: {request.decode("utf-8")}')
        sock.send(b'HI')
        
if __name__ == '__main__':
    main()

#run the server with the tcp client and it will send and return data
