import socket
import threading
import struct
import os

HOST = '127.0.0.1'
PORT = 8080
FILES_DIR = 'server_files'

os.makedirs(FILES_DIR, exist_ok=True)

def handle_client(conn, addr):
    print(f"[+] Connected: {addr}")
    try:
        while True:
            cmd = conn.recv(1024).decode().strip()
            if not cmd:
                break

            if cmd.startswith('UPLOAD'):
                _, filename = cmd.split(' ', 1)
                conn.sendall(b'READY')
                size_data = conn.recv(8)
                (file_size,) = struct.unpack('!Q', size_data)

                filepath = os.path.join(FILES_DIR, filename)
                with open(filepath, 'wb') as f:
                    remaining = file_size
                    while remaining > 0:
                        data = conn.recv(min(4096, remaining))
                        if not data:
                            break
                        f.write(data)
                        remaining -= len(data)
                print(f"[*] Received: {filename}")
                conn.sendall(b'UPLOAD OK')

            elif cmd.startswith('DOWNLOAD'):
                _, filename = cmd.split(' ', 1)
                filepath = os.path.join(FILES_DIR, filename)
                if not os.path.exists(filepath):
                    conn.sendall(b'NOFILE')
                    continue
                conn.sendall(b'READY')
                file_size = os.path.getsize(filepath)
                conn.sendall(struct.pack('!Q', file_size))
                with open(filepath, 'rb') as f:
                    while True:
                        data = f.read(4096)
                        if not data:
                            break
                        conn.sendall(data)
                print(f"[*] Sent: {filename}")

            elif cmd == 'EXIT':
                break
    except Exception as e:
        print(f"[!] Error: {e}")
    finally:
        conn.close()
        print(f"[-] Disconnected: {addr}")

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(5)
        print(f"[*] TCP Server listening on {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()
