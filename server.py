import socket
import threading
import os
from file_upload import recv_file
from file_download import send_file

def handle_client(client_socket, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    try:
        message = client_socket.recv(1024).decode('utf-8')
        if message == "HELLO":
            client_socket.send("ACK".encode('utf-8'))
            userid = client_socket.recv(1024).decode('utf-8')
            credentials = {}
            if os.path.exists("id_passwd.txt"):
                with open("id_passwd.txt", "r") as file:
                    credentials = dict(line.strip().split(":") for line in file)
                    
            correct_pwd = credentials.get(userid, "")

            client_socket.send(f"Password:{correct_pwd}".encode('utf-8'))
            response = client_socket.recv(1024).decode('utf-8')

            if response == "Password Match":
                user_dir = os.path.join("server_storage", userid)
                os.makedirs(user_dir, exist_ok=True)

                while True:
                    choice = client_socket.recv(1024).decode('utf-8')
                    if choice == '1':
                        print(f"[UPLOAD REQUEST] Receiving file from {addr}")
                        recv_file(client_socket, user_dir)
                    elif choice == '2':
                        file_name = client_socket.recv(1024).decode('utf-8')
                        print(f"[DOWNLOAD REQUEST] Sending file {file_name} to {addr}")
                        send_file(client_socket, file_name)
                    elif choice == '3':
                        print(f"[CLIENT EXIT] {addr} requested to exit.")
                        break
                    else:
                        print(f"[ERROR] Unhandled choice: {choice}")
            else:
                print(f"[LOGIN FAILED] Incorrect password for {userid}")
        else:
            print(f"[ERROR] Invalid handshake from client {addr}")
    finally:
        client_socket.close()
        print(f"[DISCONNECTED] {addr} disconnected.")

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('127.0.0.1', 8888))
    server_socket.listen()
    print("[SERVER STARTED] Listening on port 8888.")

    while True:
        client_socket, addr = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr), daemon=True)
        client_thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

if __name__ == "__main__":
    start_server()
