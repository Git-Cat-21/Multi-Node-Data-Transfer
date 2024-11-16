import os
import struct 


def download_file(client_socket,file_name,download_dir):
    if not download_dir:
        download_dir = os.getcwd()
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    try:
        client_socket.send(file_name.encode('utf-8'))

        file_size_data = client_socket.recv(8)
        if not file_size_data or int.from_bytes(file_size_data, 'big') == 0:
            print(f"Error: The file '{file_name}' does not exist on the server.")
            return
        print(file_name)
        print(download_dir)
        file_size = struct.unpack("Q", file_size_data)[0]
        file_name_from_path = os.path.basename(file_name)
        print(file_name_from_path)
        file_path = os.path.join(download_dir, file_name_from_path)

        with open(file_path, 'wb') as file:
            received_size = 0
            while received_size < file_size:
                data = client_socket.recv(1024)
                if b"<END>" in data:
                    data = data.replace(b"<END>", b"")
                    file.write(data)
                    break
                file.write(data)
                received_size += len(data)
        
        print(f"File '{file_name_from_path}' has been downloaded successfully to {file_path}.")
    
    except Exception as e:
        print(f"Error downloading file: {e}")

def send_file(client_socket, file_name):
    try:
        if os.path.isfile(file_name):
            file_size = os.path.getsize(file_name)
            client_socket.send(struct.pack("Q", file_size))  

            with open(file_name, 'rb') as file:
                while (chunk := file.read(1024)):
                    client_socket.send(chunk)
            client_socket.send(b"<END>")  
            print(f"[FILE SENT] {file_name}")
        else:
            print(f"[ERROR] File {file_name} not found.")
            client_socket.send(struct.pack("Q", 0)) 

    except Exception as e:
        print(f"[ERROR] Error sending file: {e}")