import socket
from file_upload import upload_file
from file_download import download_file
from file_preview import preview_file
import signal
import os
import struct
import sys

from logger_util import setup_logger
logger = setup_logger("ClientLogger", "logs/client.log")

def signal_handler(sig, frame):
    logger.info("[CLIENT SHUTDOWN] Signal received, closing client socket.")
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
        logger.info("[CLIENT STARTED] Attempting to connect to the server.")
        global client_socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('127.0.0.1', 8888))
        logger.info("Connected to the server.")

        try:
            initial_message = client_socket.recv(1024).decode('utf-8')
            if initial_message == "Please wait, the server is busy.":
                print("Server is busy. Please wait...")
                initial_message = client_socket.recv(1024).decode('utf-8')  
            print(initial_message)  
            logger.debug(f"Server message: {initial_message}")

            client_socket.send("HELLO".encode('utf-8'))
            response = client_socket.recv(1024).decode('utf-8')
            
            if response == "ACK":
                logger.info("Handshake successful.")
                print("Handshake successful.")
                userid = input("Username: ")
                pwd = input("Password: ")

                client_socket.send(userid.encode('utf-8'))
                password_response = client_socket.recv(1024).decode('utf-8')
                
                if password_response.startswith("Password:"):
                    correct_pwd = password_response.split(":")[1].strip()

                    if pwd == correct_pwd:
                        print("Login successful.")
                        logger.info(f"[LOGIN SUCCESS] UserID: {userid}")
                        client_socket.send("Password Match".encode("utf-8"))
                        count = 0
                        while True:
                            print("1.Upload\t2.Download\t3.Preview(First 1024 bytes only)\t4.Delete File\t5. List Directory\t6.Exit")
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
                                    logger.info(f"File uploaded: {file_name}")
                                elif choice == '2':
                                    file_name = input("Enter the file name to download (with full path): ")
                                    download_dir = input("Enter the directory to save the file: ")
                                    download_file(client_socket, file_name, download_dir)
                                    logger.info(f"File downloaded: {file_name}")
                                elif choice == '3':
                                    file_path = input("Enter the path of the file to preview: ")
                                    preview_file(client_socket, file_path)
                                    logger.info(f"File previewed: {file_path}")
                                elif choice == '4':
                                    file_name = input("Enter the name of the file to delete: ")
                                    client_socket.send(file_name.encode('utf-8'))
                                    response = client_socket.recv(1024).decode('utf-8')
                                    print(response)
                                    logger.info(f"File deleted: {file_name}")
                                elif choice == '5':
                                    print("Directory listing:")
                                    response = client_socket.recv(4096).decode('utf-8')
                                    print(response)
                                    logger.info(f"directory listed")
                                elif choice == '6':
                                    print("Exiting the client.")
                                    logger.info("Exiting the client.")
                                    break
                                else:
                                    print("Invalid choice. Please select from 1 to 6.")
                                    logger.warning(f"Invalid choice: {choice}")
                            except (ConnectionAbortedError, ConnectionResetError):
                                print("\n[ERROR] Connection to the server was lost.")
                                break
                    else:
                        print("Login failed: Password does not match.")
                        logger.warning(f"[LOGIN FAILED] Incorrect password for UserID: {userid}.")
                else:
                    print("Login failed: User not found.")
            else:
                print("Handshake failed.")
                logger.error("Handshake failed.")
        except (ConnectionAbortedError, ConnectionResetError) as e:
            print(f"\n[ERROR] Connection error: {str(e)}")
            logger.error(f"[ERROR] {str(e)}")
        finally:
            client_socket.close()
            logger.info("Client socket closed.")
        retry = input("Do you want to try logging in again? (yes/no): ").strip().lower()
        if retry != 'yes':
            break

if __name__ == "__main__":
    main()
