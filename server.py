import socket
import threading

def handle_client(client_socket, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    
    try:
        # Initial handshake: expecting "HELLO" message
        message = client_socket.recv(1024).decode('utf-8')
        if message == "HELLO":
            client_socket.send("ACK".encode('utf-8'))  # Send acknowledgment
            print(f"Connection successful with {addr}")
            
            # Data transfer after handshake
            while True:
                data = client_socket.recv(1024).decode('utf-8')
                #print(data)
                file = open("id_passwd.txt","r")
                text = file.read()
                for i in text.split():
                    if i.split(":")[0] == data:
                        pwd = i.split(":")[1]
                print(pwd)
                if not data:  # No data means client disconnected
                    break
                print(f"Received from [{addr}]: {data}")
                
                # Echo back data
                client_socket.send(f"Echo: {pwd}".encode('utf-8'))
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

        # Optional: Keep track of threads
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

start_server()
