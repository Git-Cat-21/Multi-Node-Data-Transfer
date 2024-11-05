import socket
import threading
import os

def recv_file(client_socket, addr):
    while True:
        file_name = client_socket.recv(1024).decode()
        if not file_name:
            break
        print("Receiving file:", file_name)

        file_size = client_socket.recv(1024).decode()
        print("File size:", file_size)

        with open(file_name, "wb") as file:
            
            data = client_socket.recv(1024)
            if b"<END>" in data:
                data = data.replace(b"<END>", b"")
                file.write(data)
                # bytes_received += len(data)
                break
            file.write(data)
                
        print(f"[FILE RECEIVED] {file_name} from {addr}")

def handle_client(client_socket, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    try:
        # Initial handshake
        message = client_socket.recv(1024).decode('utf-8')
        if message == "HELLO":
            client_socket.send("ACK".encode('utf-8'))  # Send acknowledgment
            print(f"Connection successful with {addr}")

            # Data transfer after handshake
            while True:
                userid = client_socket.recv(1024).decode('utf-8')
                if not userid:
                    break
                print(f"Received from [{addr}]: {userid}")

                with open("id_passwd.txt", "r") as file:
                    credentials = dict(line.strip().split(":") for line in file)
                pwd = credentials.get(userid, "")

                client_socket.send(f"Password:{pwd}".encode('utf-8'))
                choice_of_user = client_socket.recv(1024).decode('utf-8')

                if choice_of_user == '1':
                    print("Receiving file upload request")
                    recv_file(client_socket, addr)
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
            client_socket.send("Invalid handshake".encode('utf-8'))
            print(f"[HANDSHAKE FAILED] Handshake failed with {addr}")
    finally:
        client_socket.close()
        print(f"[DISCONNECTED] {addr} disconnected.")

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 12345))
    server_socket.listen()
    print("[SERVER STARTED] Listening on port 12345")

    while True:
        client_socket, addr = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

start_server()
