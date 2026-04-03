import socket
import os
import zipfile
import sys
import threading
import time

SERVER_HOST = "0.0.0.0"
SERVER_PORT = 443
BUFFER_SIZE = 4096
SAVE_DIR = os.path.join(os.path.expanduser("~"), "Downloads")

def spinner_task(stop_event, message):
    chars = ['|', '/', '-', '\\']
    idx = 0
    while not stop_event.is_set():
        sys.stdout.write(f"\r{message} {chars[idx % 4]}")
        sys.stdout.flush()
        idx += 1
        time.sleep(0.1)
    sys.stdout.write("\r" + " " * (len(message) + 2) + "\r")

def start_receiver():
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        sock.bind((SERVER_HOST, SERVER_PORT))
        sock.listen(1)
        print(f"[*] Waiting for connection on port {SERVER_PORT}...")

        client_sock, address = sock.accept()
        print(f"[+] Connected to Source: {address}")

        # 1. Get filename
        zip_name = client_sock.recv(BUFFER_SIZE).decode('utf-8')
        zip_path = os.path.join(SAVE_DIR, zip_name)
        
        # 2. Receive data
        print(f"[+] Receiving data stream...")
        with open(zip_path, "wb") as f:
            while True:
                bytes_read = client_sock.recv(BUFFER_SIZE)
                if not bytes_read:
                    break
                f.write(bytes_read)

        # 3. Extract with Spinner
        extract_to = os.path.join(SAVE_DIR, zip_name.replace(".zip", ""))
        stop_spinner = threading.Event()
        spinner_thread = threading.Thread(target=spinner_task, args=(stop_spinner, "[*] Extracting folder contents"))
        
        spinner_thread.start()
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
        finally:
            stop_spinner.set()
            spinner_thread.join()

        os.remove(zip_path) # Clean up zip
        
        print("\n" + "="*40)
        print("[SUCCESS] Folder Received!")
        print(f"[LOCATION] {os.path.abspath(extract_to)}")
        print("="*40)

    except Exception as e:
        print(f"\n[!] Error: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    start_receiver()