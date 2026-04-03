import socket
import os
import shutil
import threading
import sys
import time

# --- CONFIGURATION ---
TARGET_IP = "192.168.0.109"  # Update to Target's IP
PORT = 443
#FOLDER_TO_SEND = r"C:\Path\To\Your\Folder" 
FOLDER_TO_SEND = r"C:\ExpoNow\1A_pythonangela\1_Python_HelloWorld-utilities\utlities_Sep17_2025" 

BUFFER_SIZE = 4096

def spinner_task(stop_event, message):
    chars = ['|', '/', '-', '\\']
    idx = 0
    while not stop_event.is_set():
        sys.stdout.write(f"\r{message} {chars[idx % 4]}")
        sys.stdout.flush()
        idx += 1
        time.sleep(0.1)
    sys.stdout.write("\r" + " " * (len(message) + 2) + "\r")

def send_folder():
    if not os.path.isdir(FOLDER_TO_SEND):
        print(f"[-] Error: {FOLDER_TO_SEND} is not a folder.")
        return

    # 1. Compress with Spinner
    folder_name = os.path.basename(FOLDER_TO_SEND.rstrip(os.sep))
    stop_spinner = threading.Event()
    spinner_thread = threading.Thread(target=spinner_task, args=(stop_spinner, f"[*] Compressing '{folder_name}'"))
    
    spinner_thread.start()
    try:
        shutil.make_archive(folder_name, 'zip', FOLDER_TO_SEND)
    finally:
        stop_spinner.set()
        spinner_thread.join()
    
    zip_file = f"{folder_name}.zip"
    file_size = os.path.getsize(zip_file)

    # 2. Connect and Send
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        print(f"[+] Connecting to {TARGET_IP}...")
        sock.connect((TARGET_IP, PORT))

        # Send filename
        sock.send(zip_file.encode())
        time.sleep(1) # Ensure buffer separation

        print(f"[+] Sending {zip_file} ({file_size / (1024*1024):.2f} MB)...")
        bytes_sent = 0
        with open(zip_file, "rb") as f:
            while True:
                bytes_read = f.read(BUFFER_SIZE)
                if not bytes_read:
                    break
                sock.sendall(bytes_read)
                bytes_sent += len(bytes_read)
                # Quick progress update
                sys.stdout.write(f"\r    Progress: {(bytes_sent/file_size)*100:.1f}%")
                sys.stdout.flush()
        
        print(f"\n[SUCCESS] Transfer complete.")

    except Exception as e:
        print(f"\n[-] Error: {e}")
    finally:
        sock.close()
        if os.path.exists(zip_file):
            os.remove(zip_file)

if __name__ == "__main__":
    send_folder()