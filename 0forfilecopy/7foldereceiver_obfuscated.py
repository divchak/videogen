import socket, os, base64, zipfile

SERVER_PORT = 8443
SAVE_DIR = os.path.join(os.path.expanduser("~"), "Downloads")

def start_receiver():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("0.0.0.0", SERVER_PORT))
    sock.listen(1)
    print(f"[*] Awaiting stream on {SERVER_PORT}...")

    conn, addr = sock.accept()
    try:
        # 1. Read Header until newline
        header_data = b""
        while b"\n" not in header_data:
            header_data += conn.recv(1)
        
        header_str = header_data.decode().strip()
        name_b64, data_len = header_str.split('|')
        data_len = int(data_len)
        zip_name = base64.b64decode(name_b64).decode()
        zip_path = os.path.join(SAVE_DIR, zip_name)

        # 2. Read exactly data_len bytes
        print(f"[+] Receiving {zip_name}...")
        payload = b""
        while len(payload) < data_len:
            packet = conn.recv(8192)
            if not packet: break
            payload += packet

        # 3. Decode and Extract
        with open(zip_path, "wb") as f:
            f.write(base64.b64decode(payload))

        extract_to = os.path.join(SAVE_DIR, zip_name.replace(".zip", ""))
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(extract_to)
        
        os.remove(zip_path)
        print(f"[DONE] Folder extracted to: {os.path.abspath(extract_to)}")
    finally:
        conn.close()
        sock.close()

if __name__ == "__main__":
    start_receiver()