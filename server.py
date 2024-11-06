import socket
import threading
import os
import struct

def recv_file(client_socket, user_dir):
    try:
        while True:
            name_len_data = client_socket.recv(4)
            if not name_len_data:
                break
            name_len = struct.unpack("I", name_len_data)[0]

            file_name = client_socket.recv(name_len).decode()
            file_path = os.path.join(user_dir, file_name)

            file_size_data = client_socket.recv(8)
            file_size = struct.unpack("Q", file_size_data)[0]
            received_size = 0

            with open(file_path, "wb") as file:
                while received_size < file_size:
                    data = client_socket.recv(1024)
                    if b"<END>" in data:
                        data = data.replace(b"<END>", b"")
                        file.write(data)
                        break
                    file.write(data)
                    received_size += len(data)

            print(f"[FILE RECEIVED] {file_name}")
    except Exception as e:
        print(f"Error receiving file: {e}")

def handle_client(client_socket, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    try:
        # Initial handshake
        message = client_socket.recv(1024).decode('utf-8')
        if message == "HELLO":
            client_socket.send("ACK".encode('utf-8'))
            userid = client_socket.recv(1024).decode('utf-8')

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
                        print("Receiving file upload request.")
                        recv_file(client_socket, user_dir)
                    elif choice == '6':
                        print("Client disconnected.")
                        break
                    else:
                        print(f"Unhandled choice: {choice}")
            else:
                print("Login failed.")
        else:
            print("Invalid handshake from client.")
    finally:
        client_socket.close()
        print(f"[DISCONNECTED] {addr} disconnected.")

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 8888))
    server_socket.listen()
    print("[SERVER STARTED] Listening on port 8888.")

    while True:
        client_socket, addr = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

if __name__ == "__main__":
    start_server()
