import socket
import os
import struct
import signal
import sys

def upload_file(client_socket):
    count = 0
    while True:
        file_name = input("Enter the file location (or type 'exit' to quit): ")
        if file_name.lower() == 'exit':
            print("Exiting the file upload.")
            break
        if not os.path.isfile(file_name):
            print("File does not exist. Please try again.")
            continue

        count += 1
        file_size = os.path.getsize(file_name)
        file_ext = input("Enter the extension of the file (e.g., .txt): ")
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
        except Exception as e:
            print(f"Error sending file: {e}")
            break
    
def signal_handler(sig, frame):
    print("\n[CLIENT SHUTDOWN] Signal received, closing client socket...")
    client_socket.close()
    sys.exit(0)

# Attach the signal handler to SIGINT
signal.signal(signal.SIGINT, signal_handler)

def main():
    global client_socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('127.0.0.1', 8888))

    try:
        # Initial handshake
        client_socket.send("HELLO".encode('utf-8'))
        response = client_socket.recv(1024).decode('utf-8')
        if response == "ACK":
            print("Handshake successful.")
            userid = input("Username: ")
            pwd = input("Password: ")

            client_socket.send(userid.encode('utf-8'))
            password_response = client_socket.recv(1024).decode('utf-8')
            correct_pwd = password_response.split(":")[1].strip()

            if pwd == correct_pwd:
                print("Login successful.")
                client_socket.send("Password Match".encode("utf-8"))

                while True:
                    print("1.Upload\t2.Download\t3.View\t4.Delete\t5.List\t6.Exit : ")
                    choice = input("Enter your choice: ")
                    client_socket.send(choice.encode('utf-8'))

                    if choice == '1':
                        upload_file(client_socket)
                    elif choice == '6':
                        print("Exiting the client.")
                        break
                    else:
                        print("Functionality for this option is not implemented yet.")
            else:
                print("Login failed: Password does not match.")
        else:
            print("Handshake failed.")
    finally:
        client_socket.close()

if __name__ == "__main__":
    main()
