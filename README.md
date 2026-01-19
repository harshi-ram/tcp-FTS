# tcp-FTS
TCP/IP file transfer system in Python featuring a multithreaded server and a Tkinter GUI client. It allows for reliable uploads and downloads using chunked data transfer and binary size headers.

Features:
- Reliable file transfer with TCP/IP server
- Multithreaded server to handle multiple clients concurrently
- Binary file size headers for accurate transfer
- Chunked I/O for memory efficient file handling
- Connection and Disconnection to Server

Technologies Used:
- Python
- TCP/IP Sockets
- Threading
- Tkinter

Project Structure:

|tcp-FTS
  | tcp_client.py (GUI-based client)
  | tcp_server.py (Multithreaded TCP server)
  | server_files (where uploaded files are stored)

Running the Project:
1. Go to project root directory on the command line.
2. Start the server through the command:
    py tcp_server.py
3. Start the client through the command:
    py tcp_client.py


