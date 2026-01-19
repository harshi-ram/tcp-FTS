import socket
import struct
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

HOST = '127.0.0.1'
PORT = 8080

class FileTransferClient:
    def __init__(self, master):
        self.master = master
        master.title("TCP File Transfer Client")
        master.geometry("500x400")
        master.resizable(False, False)
        master.config(bg="#eef")

        self.sock = None

        tk.Label(master, text="TCP File Transfer Client", font=("Arial", 16, "bold"), bg="#eef").pack(pady=10)

        self.connect_btn = tk.Button(master, text="Connect to Server", width=20, command=self.connect_server, bg="#4477ff", fg="white")
        self.connect_btn.pack(pady=5)

        tk.Label(master, text="Download filename:", bg="#eef").pack(pady=(15, 0))
        self.filename_entry = tk.Entry(master, width=40)
        self.filename_entry.pack(pady=5)

        frame = tk.Frame(master, bg="#eef")
        frame.pack(pady=10)

        self.upload_btn = tk.Button(frame, text="Upload File", width=15, command=self.upload_file, bg="#44bb44", fg="white")
        self.upload_btn.grid(row=0, column=0, padx=5)

        self.download_btn = tk.Button(frame, text="Download File", width=15, command=self.download_file, bg="#ffaa00", fg="white")
        self.download_btn.grid(row=0, column=1, padx=5)

        self.exit_btn = tk.Button(frame, text="Exit", width=15, command=self.close_client, bg="#ff5555", fg="white")
        self.exit_btn.grid(row=0, column=2, padx=5)

        tk.Label(master, text="Logs:", bg="#eef").pack(pady=(10, 0))
        self.log_box = scrolledtext.ScrolledText(master, width=58, height=10, state='disabled', bg="#f9f9ff")
        self.log_box.pack(pady=5)

    def log(self, message):
        self.log_box.config(state='normal')
        self.log_box.insert(tk.END, message + '\n')
        self.log_box.yview(tk.END)
        self.log_box.config(state='disabled')

    def connect_server(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((HOST, PORT))
            self.log(f"[+] Connected to {HOST}:{PORT}")
            self.connect_btn.config(state='disabled', text="Connected")
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))

    def upload_file(self):
        if not self.sock:
            messagebox.showwarning("Not Connected", "Please connect to the server first.")
            return

        file_path = filedialog.askopenfilename()
        if not file_path:
            return

        threading.Thread(target=self._upload_thread, args=(file_path,), daemon=True).start()

    def _upload_thread(self, file_path):
        try:
            filename = os.path.basename(file_path)
            self.sock.sendall(f"UPLOAD {filename}".encode())
            if self.sock.recv(5) != b'READY':
                self.log("Server not ready for upload.")
                return
            file_size = os.path.getsize(file_path)
            self.sock.sendall(struct.pack('!Q', file_size))
            with open(file_path, 'rb') as f:
                while True:
                    data = f.read(4096)
                    if not data:
                        break
                    self.sock.sendall(data)
            msg = self.sock.recv(1024).decode()
            self.log(f"Upload complete: {filename} ({msg})")
        except Exception as e:
            self.log(f"Upload failed: {e}")

    def download_file(self):
        if not self.sock:
            messagebox.showwarning("Not Connected", "Please connect to the server first.")
            return

        filename = self.filename_entry.get().strip()
        if not filename:
            messagebox.showinfo("Missing Filename", "Please enter a filename to download.")
            return

        threading.Thread(target=self._download_thread, args=(filename,), daemon=True).start()

    def _download_thread(self, filename):
        try:
            self.sock.sendall(f"DOWNLOAD {filename}".encode())
            resp = self.sock.recv(6)
            if resp == b'NOFILE':
                self.log(f"File not found on server: {filename}")
                return
            elif resp != b'READY':
                self.log("Unexpected server response.")
                return

            size_data = self.sock.recv(8)
            (file_size,) = struct.unpack('!Q', size_data)
            save_path = f"downloaded_{filename}"
            with open(save_path, 'wb') as f:
                remaining = file_size
                while remaining > 0:
                    data = self.sock.recv(min(4096, remaining))
                    if not data:
                        break
                    f.write(data)
                    remaining -= len(data)
            self.log(f"Downloaded and saved as {save_path}")
        except Exception as e:
            self.log(f"Download failed: {e}")

    def close_client(self):
        try:
            if self.sock:
                self.sock.sendall(b'EXIT')
                self.sock.close()
            self.master.destroy()
        except:
            self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = FileTransferClient(root)
    root.mainloop()
