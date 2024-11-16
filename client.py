import socket
from file_upload import upload_file
from file_download import download_file
from file_preview import preview_file
import signal
import os
import struct
import sys

def signal_handler(sig, frame):
    print("\n[CLIENT SHUTDOWN] Signal received, closing client socket...")
    client_socket.close()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
'''

def main():
    while True:
        global client_socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('127.0.0.1', 8888))

        try:
            initial_message = client_socket.recv(1024).decode('utf-8')
            if initial_message == "Please wait, the server is busy.":
                print("Server is busy. Please wait...")
                initial_message = client_socket.recv(1024).decode('utf-8')  
            print(initial_message)  

            client_socket.send("HELLO".encode('utf-8'))
            response = client_socket.recv(1024).decode('utf-8')
            
            if response == "ACK":
                print("Handshake successful.")
                userid = input("Username: ")
                pwd = input("Password: ")

                client_socket.send(userid.encode('utf-8'))
                password_response = client_socket.recv(1024).decode('utf-8')
                
                if password_response.startswith("Password:"):
                    correct_pwd = password_response.split(":")[1].strip()

                    if pwd == correct_pwd:
                        print("Login successful.")
                        client_socket.send("Password Match".encode("utf-8"))
                        count = 0
                        while True:
                            print("1.Upload\t2.Download\t3.Preview(First 1024 bytes only)\t4.Exit")
                            choice = input("Enter your choice: ")
                            client_socket.send(choice.encode('utf-8'))

                            timeout_message = client_socket.recv(1024).decode('utf-8')
                            print(timeout_message)
                            if timeout_message == "TIMEOUT":
                                print("\n[TIMEOUT] You have been logged out due to inactivity.")
                                break  # Exit the input loop on timeout
                            
                            if timeout_message == "PROCEED":
                                print("[DEBUG] Server ready to proceed.")

                            if choice == '1':
                                file_name = input("Enter the file location (or type 'exit' to cancel upload): ")
                                if file_name.lower() == 'exit':
                                    print("Canceled the upload.")
                                    break  
                                count += 1
                                upload_file(client_socket, file_name, count)
                            elif choice == '2':
                                file_name = input("Enter the file name to download (with full path): ")
                                download_dir = input("Enter the directory to save the file: ")
                                download_file(client_socket, file_name, download_dir)
                            elif choice == '3':
                                file_path = input("Enter the path of the file to preview: ")
                                preview_file(client_socket,file_path)
                            elif choice == '4':
                                print("Exiting the client.")
                                break
                            else:
                                print("Invalid choice. Please select 1, 2, or 3.")
                    else:
                        print("Login failed: Password does not match.")
                else:
                    print("Login failed: User not found.")
            else:
                print("Handshake failed.")
        finally:
            client_socket.close()
        retry = input("Do you want to try logging in again? (yes/no): ").strip().lower()
        if retry != 'yes':
            break    
    
'''


def main():
    while True:
        global client_socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('127.0.0.1', 8888))

        try:
            initial_message = client_socket.recv(1024).decode('utf-8')
            if initial_message == "Please wait, the server is busy.":
                print("Server is busy. Please wait...")
                initial_message = client_socket.recv(1024).decode('utf-8')  
            print(initial_message)  

            client_socket.send("HELLO".encode('utf-8'))
            response = client_socket.recv(1024).decode('utf-8')
            
            if response == "ACK":
                print("Handshake successful.")
                userid = input("Username: ")
                pwd = input("Password: ")

                client_socket.send(userid.encode('utf-8'))
                password_response = client_socket.recv(1024).decode('utf-8')
                
                if password_response.startswith("Password:"):
                    correct_pwd = password_response.split(":")[1].strip()

                    if pwd == correct_pwd:
                        print("Login successful.")
                        client_socket.send("Password Match".encode("utf-8"))
                        count = 0
                        while True:
                            print("1.Upload\t2.Download\t3.Preview(First 1024 bytes only)\t4.Exit")
                            choice = input("Enter your choice: ")
                            client_socket.send(choice.encode('utf-8'))

                            try:
                                timeout_message = client_socket.recv(1024).decode('utf-8')
                                print(timeout_message)
                                if timeout_message == "TIMEOUT":
                                    print("\n[TIMEOUT] You have been logged out due to inactivity.")
                                    break  # Exit the input loop on timeout
                                
                                #if timeout_message == "PROCEED":
                                #    print("[DEBUG] Server ready to proceed.")

                                if choice == '1':
                                    file_name = input("Enter the file location (or type 'exit' to cancel upload): ")
                                    if file_name.lower() == 'exit':
                                        print("Canceled the upload.")
                                        break  
                                    count += 1
                                    upload_file(client_socket, file_name, count)
                                elif choice == '2':
                                    file_name = input("Enter the file name to download (with full path): ")
                                    download_dir = input("Enter the directory to save the file: ")
                                    download_file(client_socket, file_name, download_dir)
                                elif choice == '3':
                                    file_path = input("Enter the path of the file to preview: ")
                                    preview_file(client_socket, file_path)
                                elif choice == '4':
                                    print("Exiting the client.")
                                    break
                                else:
                                    print("Invalid choice. Please select 1, 2, or 3.")
                            except (ConnectionAbortedError, ConnectionResetError):
                                print("\n[ERROR] Connection to the server was lost.")
                                break
                    else:
                        print("Login failed: Password does not match.")
                else:
                    print("Login failed: User not found.")
            else:
                print("Handshake failed.")
        except (ConnectionAbortedError, ConnectionResetError) as e:
            print(f"\n[ERROR] Connection error: {str(e)}")
        finally:
            client_socket.close()
        retry = input("Do you want to try logging in again? (yes/no): ").strip().lower()
        if retry != 'yes':
            break

if __name__ == "__main__":
    main()
