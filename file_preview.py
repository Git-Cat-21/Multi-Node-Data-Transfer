import os
import struct

def preview_file(client_socket, file_name, userid):
    try:
        
        file_path = f"./server_storage/{userid}/{file_name}"
        print(f"[DEBUG] Requesting preview for: {file_path}")
        client_socket.send(file_path.encode('utf-8'))
        
        # Receive the file size
        file_size_data = client_socket.recv(8)
        file_size = struct.unpack("Q", file_size_data)[0]  # Unpack the size
        
        if file_size == 0:
            print(f"Error: The file '{file_name}' does not exist on the server.")
            return

        
        preview_data = b""
        while True:
            data = client_socket.recv(1024)
            if b"<END>" in data:  
                preview_data += data.replace(b"<END>", b"")
                break
            preview_data += data

        print(f"File Preview (First 1024 bytes):\n{preview_data.decode('utf-8', errors='ignore')}")

    except Exception as e:
        print(f"Error previewing file: {e}")

def send_preview(client_socket, file_path):
    """Sends the first 1024 bytes of the file for preview."""
    try:
        print(f"[DEBUG] Checking file: {file_path}")
        if os.path.isfile(file_path):
            file_size = os.path.getsize(file_path)
            client_socket.send(struct.pack("Q", file_size))  
            
            with open(file_path, 'rb') as file:
                file_data = file.read(1024)  
            client_socket.send(file_data)  
            client_socket.send(b"<END>")  
            print(f"[PREVIEW SENT] {file_path}")
        else:
            client_socket.send(struct.pack("Q", 0))  
            print(f"[ERROR] File '{file_path}' does not exist.")
    except Exception as e:
        client_socket.send(struct.pack("Q", 0))  
        print(f"[ERROR] Error sending preview: {e}")
