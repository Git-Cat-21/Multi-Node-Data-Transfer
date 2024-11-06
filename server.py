import socket
import threading
import os
import struct

def recv_file(client_socket, addr, user_dir):
    while True:
        try:
            name_len_data = client_socket.recv(4)
            if not name_len_data:
                break
            name_len = struct.unpack("I", name_len_data)[0]
            
            file_name = client_socket.recv(name_len).decode()
            print("Receiving file:", file_name)

            file_path = os.path.join(user_dir, file_name)
            print("File path:", file_path)

            file_size_data = client_socket.recv(8)
            file_size = struct.unpack("Q", file_size_data)[0]
            print("File size:", file_size)

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
                
            print(f"[FILE RECEIVED] {file_name} from {addr}")
        except Exception as e:
            print(f"Error receiving file: {e}")
            break

def handle_client(client_socket, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    try:
        # Initial handshake
        message = client_socket.recv(1024).decode('utf-8')
        if message == "HELLO":
            client_socket.send("ACK".encode('utf-8'))  # Send acknowledgment
            print(f"Connection successful with {addr}")

            userid = client_socket.recv(1024).decode('utf-8')
            print(f"Received User ID [{addr}]: {userid}")

            with open("id_passwd.txt", "r") as file:
                credentials = dict(line.strip().split(":") for line in file)
            pwd = credentials.get(userid, "")

            client_socket.send(f"Password:{pwd}".encode('utf-8'))

            response = client_socket.recv(1024).decode('utf-8')
            if response == "Password Match":
                user_dir = os.path.join("server_storage", userid)
                if not os.path.exists(user_dir):
                    os.makedirs(user_dir)
                    print(f"Directory created for user: {userid}")

                while True:
                    choice_of_user = client_socket.recv(1024).decode('utf-8')

                    if choice_of_user == '1':
                        print("Receiving file upload request")
                        recv_file(client_socket, addr, user_dir)
                    elif choice_of_user == '2':
                        print("Download request")
                    elif choice_of_user == '3':
                        print("View request")
                    elif choice_of_user == '4':
                        print("Delete request")
                    elif choice_of_user == '5':
                        print("List files request")
                    elif choice_of_user == '6':
                        print("Exit request")
                        break
                    else:
                        print("Invalid choice received")
            else:
                print("Login failed for user:", userid)
                client_socket.send("Login failed".encode('utf-8'))
        else:
            client_socket.send("Invalid handshake".encode('utf-8'))
            print(f"[HANDSHAKE FAILED] Handshake failed with {addr}")
    finally:
        client_socket.close()
        print(f"[DISCONNECTED] {addr} disconnected.")

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 8888))
    server_socket.listen()
    print("[SERVER STARTED] Listening on port 8888")

    while True:
        client_socket, addr = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

start_server()
