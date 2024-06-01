import board
import time
import os
import gc

display = board.DISPLAY
requests = None


def load_module(module_name):
    try:
        exec(f"import {module_name}")
        print(f"Loaded {module_name} library.")
    except ImportError as e:
        print(f"Failed to load {module_name} library: {e}")

def load_io_libs():
    print("Loading *io libraries...")
    for module_name in ["digitalio", "analogio", "busio", "displayio"]:
        load_module(module_name)
    
  
def connect_to_wifi():
    load_module("wifi")
    print("Connecting to WiFi...")
    try:
        wifi.radio.connect(os.getenv('CIRCUITPY_WIFI_SSID'), os.getenv('CIRCUITPY_WIFI_PASSWORD'))
        print(f"Connected to WiFi {os.getenv('CIRCUITPY_WIFI_SSID')}")
        return True
    except Exception as e:
        print(f"Failed to connect to WiFi: {e}")
        return False


def load_all_libs():
    print("Loading all libraries in 'lib' directory...")
    libs_dir = "/lib"
    try:
        files_and_dirs = os.listdir(libs_dir)
    except OSError:
        print(f"Directory {libs_dir} does not exist.")
        return

    for filename in files_and_dirs:
        filepath = f"{libs_dir}/{filename}"
        if filename.endswith(".py"):
            module_name = filename[:-3] 
        elif filename.endswith(".mpy"):
            module_name = filename[:-4] 
        else:
            try:
                os.listdir(filepath)
                module_name = filename
            except OSError:
                continue
        
        load_module(module_name)


def load_requests():
    global requests
    print("Loading requests library...")
    try:
        for module_name in ["adafruit_requests", "socketpool", "ssl"]:
            load_module(module_name)
        pool = socketpool.SocketPool(wifi.radio)
        requests = adafruit_requests.Session(pool, ssl.create_default_context())
        print("'requests' object created")
    except ImportError as e:
        print(f"Failed to load requests library: {e}")


def i2c_scanner():
    print("Scanning I2C bus for devices...")
    import busio
    try:
        i2c = busio.I2C(board.SCL, board.SDA)
        while not i2c.try_lock():
            pass
        try:
            devices = i2c.scan()
            if devices:
                print("I2C devices found:")
                for device in devices:
                    print(f" - I2C address: {hex(device)}")
            else:
                print("No I2C devices found")
        finally:
            i2c.unlock()
    except RuntimeError as e:
        print(f"Error: {e}")


def menu():
    wifi_connected = False
    while True:
        print("=== Quick Menu: ===")
        print("i - load common io libs")
        if not wifi_connected:
            print("w - connect to wifi")
        if wifi_connected:
            print("r - load requests library")
        print("l - import all libs in '/lib'")
        print("s - scan I2C bus for devices")
        print("q - quit menu and enter REPL")
        
        choice = input("Choose an option: ")

        if choice == "i":
            load_io_libs()
        elif choice == "w":
            wifi_connected = connect_to_wifi()
        elif choice == "r":
            load_requests()
        elif choice == "l":
            load_all_libs()
        elif choice == "s":
            i2c_scanner()
        elif choice == "q":
            print("Open menu again with menu()")
            print()
            gc.collect()
            break
        else:
            print("Invalid choice. Please try again.")
        time.sleep(1)

menu()