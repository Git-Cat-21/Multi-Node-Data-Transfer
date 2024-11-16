import socket
import os
from concurrent.futures import ThreadPoolExecutor
from file_upload import recv_file
from file_download import send_file
from file_preview import read_file
from threading import Semaphore
import threading
import struct
import signal
import sys
import time

TIMEOUT_DURATION = 15 # Timeout in seconds

MAX_CONCURRENT_CLIENTS = 2
semaphore = Semaphore(MAX_CONCURRENT_CLIENTS)

def signal_handler(sig, frame):
    print("\n[SERVER SHUTDOWN] Signal received, closing server socket...")
    server_socket.close()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def handle_client(client_socket, addr):
    if not semaphore.acquire(blocking=False):
        client_socket.send("Please wait, the server is busy.".encode('utf-8'))
        semaphore.acquire()  

    client_socket.send("You are now connected to the server.".encode('utf-8'))
    print(f"[NEW CONNECTION] {addr} connected.")
    last_active_time = time.time()

    try:
        message = client_socket.recv(1024).decode('utf-8')
        if message == "HELLO":
            client_socket.send("ACK".encode('utf-8'))
            userid = client_socket.recv(1024).decode('utf-8')
            last_active_time = time.time()

            credentials = {}
            if os.path.exists("id_passwd.txt"):
                with open("id_passwd.txt", "r") as file:
                    credentials = dict(line.strip().split(":") for line in file)
                    
            correct_pwd = credentials.get(userid, "")

            client_socket.send(f"Password:{correct_pwd}".encode('utf-8'))
            response = client_socket.recv(1024).decode('utf-8')
            last_active_time = time.time()

            if response == "Password Match":
                user_dir = os.path.join("server_storage", userid)
                os.makedirs(user_dir, exist_ok=True)

                while True:
                    client_socket.settimeout(TIMEOUT_DURATION)
                    try:
                        choice = client_socket.recv(1024).decode('utf-8')
                        last_active_time = time.time()
                        client_socket.settimeout(None)

                        # Check if there was a timeout (inactivity)
                        if time.time() - last_active_time > TIMEOUT_DURATION:
                            print(f"[TIMEOUT] {addr} inactive for {TIMEOUT_DURATION} seconds. Disconnecting...")
                            client_socket.send("TIMEOUT".encode('utf-8'))
                            break
                        else:
                            client_socket.send("PROCEED".encode('utf-8'))
                        if choice == '1':
                            print(f"[UPLOAD REQUEST] Receiving file from {addr}")
                            recv_file(client_socket, user_dir)
                        elif choice == '2':
                            file_name = client_socket.recv(1024).decode('utf-8')
                            print(f"[DOWNLOAD REQUEST] Sending file {file_name} to {addr}")
                            send_file(client_socket, file_name)
                        elif choice == '3':
                            file_path = client_socket.recv(1024).decode('utf-8')
                            print(f"[PREVIEW REQUEST] Sending file {file_path} to {addr}")
                            read_file(client_socket, file_path)
                        elif choice == '4':
                            print(f"[CLIENT EXIT] {addr} requested to exit.")
                            break
                        else:
                            print(f"[ERROR] Unhandled choice: {choice}")
                    except socket.timeout:
                        print(f"[TIMEOUT] {addr} inactive for {TIMEOUT_DURATION} seconds. Disconnecting...")
                        client_socket.send("TIMEOUT".encode('utf-8'))
                        break
            else:
                print(f"[LOGIN FAILED] Incorrect password for {userid}")
        else:
            print(f"[ERROR] Invalid handshake from client {addr}")
    finally:
        client_socket.close()
        print(f"[DISCONNECTED] {addr} disconnected.")
        semaphore.release()  

def start_server():
    global server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('127.0.0.1', 8888))
    server_socket.listen()
    print("[SERVER STARTED] Listening on port 8888.")

    with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_CLIENTS) as executor:
        while True:
            client_socket, addr = server_socket.accept()
            print(f"[CONNECTION ACCEPTED] Connection from {addr}")
            executor.submit(handle_client, client_socket, addr)


if __name__ == "__main__":
    start_server()
