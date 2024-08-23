import argparse
import socket
import shlex
import subprocess
import sys
import textwrap
import threading

def execute(cmd):#recieves a command runs it and returns the output as a string
    cmd = cmd.strip()
    if not cmd:
        return
    output = subprocess.check_output(shlex.split(cmd),stderr=subprocess.STDOUT) #the subproces library gives us the ability to interact with a client program
    #we use the check_output function to run a command on the local operating system and return the output from the command
    
    return output.decode()



class Netcat:
    def __init__(self,args,buffer_None):
        self.args = args
        self.buffer = buffer
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
        
    def run(self):
        if self.args.listen:
            self.listen()
        else:
            self.send()
            
    def send(self):
        self.socket.connect((self.args.target, self.args.port)) #connect to target and port
        if self.buffer:
            self.socket.send(self.buffer) #if there is a buffer it will be sent first
        
        try:
            while True:
                recv_len = 1
                response = ''
                while recv_len: #start a loop to recieve data from target
                    data = send.socket.recv(4096)
                    recv_len = len(data)
                    response += data.decode()
                    if recv_len < 4096:  #if there is no more data to recieve we break out
                        break
                    if response: #get the response, pause to get interactive input, send the input and continue the loop
                        print(response)
                        buffer = input('> ')
                        buffer += '\n'
                        self.socket.send(buffer.encode())
        except KeyboardInterrupt:
            print('User Terminated.')
            self.socket.close()
            sys.exit()
            
    def listen(self):
        self.socket.bind((self.args.target, self.args.port))
        self.socket.listen(5)
        
        while True: #the listen method binds to the target and port and starts listening in a loop
            client_socket, = self.socket.accept()
            client_thread = threading.Thread(target=self.handle,args=(client_socket,)) #passing the connected socket to the handle method
            client_thread.start()
    
    
    def handle(self,client_socket):#upload,execute and create command shell
        
        if self.args.execute:
            output = execute(self.args.execute) #if execute is selected the handle method passes the command to the execute function and sends it back out to the socket
            client_socket.send(output.encode())
        
        elif self.args.upload: #if upload is selected then a loop is started to listen for content and writes it down to a specified file
            file_buffer = b''
            while True:
                data = client_socket.recv(4096)
                if data:
                    file_bufer += data
                else:
                    break
                    
            with open(self.args.upload, 'wb') as f:
                f.write(file.buffer)
            message = f'Saved file {self.args.upload}'
            client_socket.send(message.encode())
            
        elif self.args.command: #if command shell is selected we start a loop, send a prompt to the sender, and wait for the command to come back. Then, the command is executed with the execute() function and the output is returned to the sender.
            cmd_buffer = b''
            while True:
                try:
                    client_socket.send(b'BHP: #> ')
                    while '\n' not in cmd_buffer.decode():#the code checks for a newline character to know when to process a command.
                        cmd_buffer += client_socket.recv(64)
                    response = execute(cmd_buffer.decode())
                    if response:
                        client_socket.send(response.encode())
                    cmd_buffer = b''
                except Exception as e:
                    print(f'server killed {e}')
                    seld.socket.close()
                    sys.exit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='BHP Net Tool', #the argparse module is used to create a command line interface
    formatter_class = argparse.RawDescriptionHelpFormatter,
    epilog=textwrap.dedent('''Example:
    netcat.py -t 192.168.1.108 -p 5555 -l -c # command shell
    netcat.py -t 192.168.1.108 -p 5555 -l -u=mytest.txt # upload a file
    netcat.py -t 192.168.1.108 -p 5555 -l -e/\"cat /etc/passwd" # execute a command
    echo 'ABC' | ./netcat.py -t 192.168.1.108 -p 5555 # connect to a server
    '''))
    #this is the example usage the interface will show when we call for --help
    
    parser.add_argument('-c','--command', action ='store_true', help='command shell')#setup 6 arguments to  spacify that actions we can pass
    parser.add_argument('-e','--execute', help='execute specified command')
    parser.add_argument('-l','--listen', action ='store_true', help='listen')
    parser.add_argument('-p','--port', type=int, default=5555, help='specified port')
    parser.add_argument('-t','--target', default='192.168.1.203', help='specified IP')
    parser.add_argument('-u','--upload', help='upload file')
    
    args = parser.parse_args()
    if args.listen: #if we set up a listener,the netcat object is invoked with an empty buffer string.
        buffer = ''
    else:
        buffer = sys.stdin.read() #otherwise we send the buffer content from stdin
       
    nc = Netcat(args,buffer.encode())
    nc.run() #starting up the netcat 
