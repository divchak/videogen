import socket, os, shutil, base64, time

# --- CONFIGURATION ---
TARGET_IP = "192.168.0.109" 
PORT = 8443
FOLDER_TO_SEND = r"C:\ExpoNow\1A_pythonangela\1_Python_HelloWorld-utilities\utlities_Sep17_2025"

def send_folder():
    print(f"[*] Analyzing folder: {FOLDER_TO_SEND}")
    
    # 1. Validation: Check if the folder actually exists
    if not os.path.isdir(FOLDER_TO_SEND):
        print(f"[-] ERROR: Folder not found at {FOLDER_TO_SEND}")
        return

    # 2. Zip the folder
    base_name = os.path.basename(FOLDER_TO_SEND.rstrip(os.sep))
    print(f"[*] Compressing '{base_name}'...")
    try:
        # This creates 'base_name.zip' in the current script directory
        zip_output = shutil.make_archive(base_name, 'zip', FOLDER_TO_SEND)
        zip_file = os.path.basename(zip_output)
    except Exception as e:
        print(f"[-] Compression failed: {e}")
        return
    
    # 3. Prepare Obfuscated Data
    print(f"[*] Encoding data for obfuscation...")
    try:
        with open(zip_file, "rb") as f:
            encoded_data = base64.b64encode(f.read())
    except Exception as e:
        print(f"[-] Read error: {e}")
        return
    
    # 4. Connect and Send
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(15) # Wait 15 seconds max for a response
    
    try:
        print(f"[*] Attempting to connect to {TARGET_IP}:{PORT}...")
        sock.connect((TARGET_IP, PORT))
        print("[+] Connected to Receiver!")
        
        # Header: filename_base64|data_length\n
        # This tells the receiver what the file is called and how much to read
        file_name_b64 = base64.b64encode(zip_file.encode()).decode()
        header = f"{file_name_b64}|{len(encoded_data)}\n".encode()
        
        print("[*] Sending header and data...")
        sock.sendall(header)
        sock.sendall(encoded_data)
        
        print(f"[SUCCESS] Folder '{base_name}' pushed successfully.")
        
    except socket.timeout:
        print("[-] ERROR: Connection timed out. Ensure Receiver is running and IP is correct.")
    except ConnectionRefusedError:
        print("[-] ERROR: Connection refused. Check Port 8443 on Receiver.")
    except Exception as e:
        print(f"[-] Unexpected Error: {e}")
    finally:
        sock.close()
        # Clean up the temporary zip file created during the process
        if os.path.exists(zip_file): 
            os.remove(zip_file)
            print("[*] Temporary zip removed.")
        
        print("[*] Script finished. sender.py remains on disk.")

if __name__ == "__main__":
    send_folder()