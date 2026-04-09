import adbutils
import time

def scan_bluestacks_ports():
    print("Testing ADB connection to common BlueStacks ports...")
    
    # Common ports for BlueStacks instances
    # Instance 0 (Main): 5555
    # Instance 1: 5565
    # Instance 2: 5575
    ports = [5555, 5565, 5575]
    
    connected_devices = []
    
    for port in ports:
        try:
            # Try to connect
            result = adbutils.adb.connect(f"127.0.0.1:{port}")
            if "connected" in result.lower() or "already" in result.lower():
                print(f"Successfully pinged a device on port {port}!")
        except Exception as e:
            pass

    print("\nScanning for active devices...")
    time.sleep(1) # Give ADB daemon a second to register
    
    devices = adbutils.adb.device_list()
    if not devices:
        print("No ADB devices found! Please ensure ADB is turned ON in BlueStacks settings.")
        return
        
    for d in devices:
        info = d.prop.name or "Unknown Device"
        print(f"Connected to: {d.serial} ({info})")

if __name__ == "__main__":
    scan_bluestacks_ports()
