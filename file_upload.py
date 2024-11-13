# file_transfer.py
import os
import struct

def upload_file(client_socket, file_name, count):
    if not os.path.isfile(file_name):
        print("File does not exist. Please try again.")
        return False

    file_size = os.path.getsize(file_name)
    file_ext = os.path.splitext(file_name)[1]
    recv_file_name = f"received_file{count}{file_ext}"

    try:
        client_socket.send(struct.pack("I", len(recv_file_name)))
        client_socket.send(recv_file_name.encode())
        client_socket.send(struct.pack("Q", file_size))

        with open(file_name, "rb") as file:
            while (data := file.read(1024)):
                client_socket.send(data)

        client_socket.send(b"<END>")
        print(f"{file_name} has been sent successfully.")
        return True
    except Exception as e:
        print(f"Error sending file: {e}")
        return False


def recv_file(client_socket, user_dir):
    try:
        name_len_data = client_socket.recv(4)
        if not name_len_data:
            return False
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
        return True
    except Exception as e:
        print(f"Error receiving file: {e}")
        return False
