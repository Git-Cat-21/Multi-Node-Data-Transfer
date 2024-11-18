import os
import struct

CHUNK_SIZE = 1024  

def upload_file(client_socket, file_name, count):

    if not os.path.isfile(file_name):
        print("File does not exist. Please try again.")
        return False

    file_size = os.path.getsize(file_name)
    file_ext = os.path.splitext(file_name)[1]
    recv_file_name = f"received_file{count}{file_ext}"

    try:
        client_socket.send(struct.pack("I", len(recv_file_name)))  # File name length
        client_socket.send(recv_file_name.encode())  # File name
        client_socket.send(struct.pack("Q", file_size))  # File size

        print(f"Uploading '{file_name}' in chunks of {CHUNK_SIZE} bytes.")

        with open(file_name, "rb") as file:
            total_sent = 0
            while (chunk := file.read(CHUNK_SIZE)):
                chunk_size = len(chunk)
                client_socket.send(struct.pack("I", chunk_size))  
                client_socket.send(chunk) 
                total_sent += chunk_size
                print(f"Uploaded {total_sent}/{file_size} bytes", end="\r")

        client_socket.send(b"<END>")
        print(f"\n{file_name} has been sent successfully.")
        return True

    except Exception as e:
        print(f"Error sending file: {e}")
        return False

def recv_file(client_socket, user_dir):
    try:
        name_len_data = client_socket.recv(4)
        name_len = struct.unpack("I", name_len_data)[0]

        file_name = client_socket.recv(name_len).decode()
        file_path = os.path.join(user_dir, file_name)

        file_size_data = client_socket.recv(8)
        file_size = struct.unpack("Q", file_size_data)[0]
        received_size = 0

        print(f"Receiving '{file_name}' ({file_size} bytes)...")

        with open(file_path, "wb") as file:
            while received_size < file_size:
                chunk_size_data = client_socket.recv(4)
                chunk_size = struct.unpack("I", chunk_size_data)[0]

                chunk = client_socket.recv(chunk_size)
                if b"<END>" in chunk:
                    chunk = chunk.replace(b"<END>", b"")
                    file.write(chunk)
                    received_size += len(chunk)
                    break

                file.write(chunk)
                received_size += len(chunk)
                print(f"Received {received_size}/{file_size} bytes", end="\r")

        print(f"\n[FILE RECEIVED] {file_name}")
        return True
    except Exception as e:
        print(f"Error receiving file: {e}")
        return False
