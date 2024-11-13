import socket
import struct
from file_upload import upload_file

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('127.0.0.1', 8888))

    try:
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

                count = 0
                while True:
                    print("1.Upload\t2.Exit")
                    choice = input("Enter your choice: ")
                    client_socket.send(choice.encode('utf-8'))

                    if choice == '1':
                        file_name = input("Enter the file location (or type 'exit' to quit): ")
                        if file_name.lower() == 'exit':
                            print("Exiting the file upload.")
                            break
                        count += 1
                        upload_file(client_socket, file_name, count)
                    elif choice == '2':
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
