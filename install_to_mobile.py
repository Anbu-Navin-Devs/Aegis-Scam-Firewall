import os
import subprocess
import time
import sys

# ==============================================================================
# 📱 AEGIS MOBILE APP - WIRELESS INSTALLER
# ==============================================================================
# Enter your Android Wireless Debugging details here before running!
# 
# How to find these details:
# 1. On your Android phone, go to Settings -> Developer Options.
# 2. Enable "Wireless Debugging" (must be on the same Wi-Fi as your PC).
# 3. Tap "Wireless Debugging" to enter the menu.
# 4. Look at "IP address & Port" -> That is your IP_ADDRESS and CONNECT_PORT.
# 5. Tap "Pair device with pairing code".
# 6. A popup will show the PAIRING_CODE and a new IP address with the PAIRING_PORT.
# ==============================================================================

IP_ADDRESS = "172.16.0.122"    # Example: "192.168.1.122"
PAIRING_PORT = "41679"         # Example: "38593"
PAIRING_CODE = "060734"        # Example: "049382"

CONNECT_PORT = "37785"         # Example: "40192"

# ==============================================================================

def run_command(command, cwd=None):
    print(f"\n> Running: {command}")
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            text=True,
            capture_output=True
        )
        print(result.stdout)
        if result.returncode != 0:
            print(f"ERROR:\n{result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"Exception: {e}")
        return False

def main():
    print("🚀 AEGIS WIRELESS APP DEPLOYMENT 🚀")
    print("=======================================")

    if IP_ADDRESS == "192.168.1.XX":
        print("❌ ERROR: Please edit 'install_to_mobile.py' and enter your IP_ADDRESS, Ports, and Pairing Code!")
        sys.exit(1)

    print("\n📡 Step 1: Checking Device Connection...")
    
    # Function to get the first attached device ID
    def get_connected_device():
        result = subprocess.run("adb devices", shell=True, capture_output=True, text=True)
        lines = result.stdout.strip().split('\n')[1:] # Skip "List of devices attached"
        for line in lines:
            if 'device' in line and 'offline' not in line and 'unauthorized' not in line:
                return line.split()[0] # Return the device ID (either IP:PORT or adb-xxx)
        return None

    device_id = get_connected_device()

    if device_id:
        print(f"✅ Device already connected: {device_id}")
    else:
        print("⚠️ No device connected. Attempting to connect...")
        connect_cmd = f"adb connect {IP_ADDRESS}:{CONNECT_PORT}"
        print(f"\n> Running: {connect_cmd}")
        subprocess.run(connect_cmd, shell=True)
        time.sleep(2)
        
        device_id = get_connected_device()
        if not device_id:
            print("⚠️ Not connected. Attempting to pair first...")
            pair_cmd = f"adb pair {IP_ADDRESS}:{PAIRING_PORT} {PAIRING_CODE}"
            print(f"\n> Running: {pair_cmd}")
            subprocess.run(pair_cmd, shell=True)
            time.sleep(2)
            print("\n> Re-trying connection...")
            subprocess.run(connect_cmd, shell=True)
            time.sleep(2)
            device_id = get_connected_device()

    if not device_id:
        print("❌ ERROR: Could not connect to any device. Please check your IP and Ports!")
        sys.exit(1)

    print(f"\n📱 Step 2: Using Device ID: {device_id}")

    frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")
    if not os.path.exists(frontend_dir):
        print("❌ ERROR: 'frontend' folder not found. Are you running this from the project root?")
        sys.exit(1)

    print("\n📦 Step 3: Ensuring Flutter is Installed...")
    
    flutter_cmd = "flutter"
    try:
        subprocess.run(["flutter", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✅ Flutter is already installed globally.")
    except FileNotFoundError:
        print("⚠️ Flutter not found in PATH. Setting it up on C:\\ for global use...")
        flutter_sdk_dir = "C:\\flutter_sdk"
        flutter_bat = os.path.join(flutter_sdk_dir, "flutter", "bin", "flutter.bat")
        
        if not os.path.exists(flutter_sdk_dir):
            import urllib.request
            import zipfile
            
            try:
                os.makedirs(flutter_sdk_dir, exist_ok=True)
            except PermissionError:
                print("❌ ERROR: Permission denied creating C:\\flutter_sdk. Please run terminal as Administrator!")
                sys.exit(1)

            zip_path = os.path.join(flutter_sdk_dir, "flutter.zip")
            
            print("\n📥 Downloading Flutter SDK to C:\\ (this is faster!)...")
            flutter_url = "https://storage.googleapis.com/flutter_infra_release/releases/stable/windows/flutter_windows_3.24.3-stable.zip"
            
            def download_progress(count, block_size, total_size):
                percent = int(count * block_size * 100 / total_size)
                sys.stdout.write(f"\rDownloading... {percent}%")
                sys.stdout.flush()

            urllib.request.urlretrieve(flutter_url, zip_path, reporthook=download_progress)
            print("\n✅ Download complete!")
            
            print("📦 Extracting Flutter SDK to C:\\...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(flutter_sdk_dir)
            
            print("🧹 Cleaning up zip file...")
            os.remove(zip_path)
            
            print("⏳ Initializing Flutter (setting up core tools)...")
            subprocess.run(f'"{flutter_bat}" doctor', shell=True)
            
        flutter_cmd = f'"{flutter_bat}"'
        print(f"✅ Flutter is now available at {flutter_bat}")

    print("\n📦 Step 4: Installing Aegis App via Flutter...")
    print("Building and deploying APK to your mobile device. This may take a few minutes...")
    
    run_app_cmd = f"{flutter_cmd} run -d {device_id}"
    
    print(f"\n> Running: {run_app_cmd} in {frontend_dir}")
    try:
        subprocess.run(run_app_cmd, shell=True, cwd=frontend_dir)
    except KeyboardInterrupt:
        print("\nDeployment stopped by user.")
        
    print("\n✅ Deployment process finished!")

if __name__ == "__main__":
    main()
