import os
import struct 

def download_file(client_socket, file_name, download_dir, userid):
    if not download_dir:
        download_dir = os.getcwd()
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    try:
       
        client_socket.send(f"./server_storage/{userid}/{file_name}".encode('utf-8'))
        file_size_data = client_socket.recv(8)
        # print(file_size_data)
        if not file_size_data or len(file_size_data) != 8:
            print(f"Error: Did not receive a valid file size for '{file_name}'.")
            return

        file_size = struct.unpack("Q", file_size_data)[0]
        if file_size == 0:
            print(f"Error: The file '{file_name}' does not exist on the server.")
            return

        file_name_from_path = os.path.basename(file_name)
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


def send_file(client_socket, file_path):
    try:
        if os.path.isfile(file_path):
            file_size = os.path.getsize(file_path)
            client_socket.send(struct.pack("Q", file_size))  
            
            with open(file_path, "rb") as file:
                while (chunk := file.read(1024)):
                    client_socket.send(chunk)
            
            client_socket.send(b"<END>")  
            print(f"[FILE SENT] {file_path}")
        else:
            client_socket.send(struct.pack("Q", 0)) 
            print(f"[ERROR] File not found: {file_path}")
    except Exception as e:
        print(f"[ERROR] Error sending file: {e}")
