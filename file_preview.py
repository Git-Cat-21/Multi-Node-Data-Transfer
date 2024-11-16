import os
import struct

def preview_file(client_socket, file_path):
    client_socket.send(file_path.encode('utf-8'))
    preview_data = client_socket.recv(1024)
    if preview_data:
        preview_message = preview_data.decode('utf-8', errors='ignore')
        if preview_message.startswith("File"):
            print(preview_message)
        else:
            print(f"File Preview (First 1024 bytes):\n{preview_message}")
    else:
        print("Failed to retrieve file preview. The file may not exist on the server.")
 

def read_file(client_socket,file_path):
    if os.path.isfile(file_path):
        with open(file_path, 'rb') as file:
            file_data = file.read(1024)
        client_socket.send(file_data)
        print(f"[SERVER] Sent first 1024 bytes of {file_path} to the client.")
    else:
        error_message = f"File '{file_path}' does not exist."
        client_socket.send(error_message.encode('utf-8'))
