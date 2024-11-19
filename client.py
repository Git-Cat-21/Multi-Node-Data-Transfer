import socket
from file_upload import upload_file
from file_download import download_file
from file_preview import preview_file
import signal
import os
import struct
import sys
import maskpass

from logger_util import setup_logger
logger = setup_logger("ClientLogger", "logs/client.log")

def signal_handler(sig, frame):
    logger.info("[CLIENT SHUTDOWN] Signal received, closing client socket.")
    print("\n[CLIENT SHUTDOWN] Signal received, closing client socket...\n")
    client_socket.close()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def main():
    restart = True
    while restart:
        logger.info("[CLIENT STARTED] Attempting to connect to the server.")
        global client_socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('127.0.0.1', 8888))
        logger.info("Connected to the server.")

        try:
            initial_message = client_socket.recv(1024).decode('utf-8')
            if initial_message == "Please wait, the server is busy.":
                print("\n[INFO] Server is busy. Please wait...\n")
                initial_message = client_socket.recv(1024).decode('utf-8')
            print(f"\n{initial_message}\n")
            logger.debug(f"Server message: {initial_message}")

            client_socket.send("HELLO".encode('utf-8'))
            response = client_socket.recv(1024).decode('utf-8')
            
            if response == "ACK":
                logger.info("Handshake successful.")
                print("\n[INFO] Handshake successful.\n")
                userid = input("Username: ")
                pwd = maskpass.askpass(mask="*")  
                print("\n")

                client_socket.send(userid.encode('utf-8'))
                password_response = client_socket.recv(1024).decode('utf-8')
                
                if password_response.startswith("Password:"):
                    correct_pwd = password_response.split(":")[1].strip()

                    if pwd == correct_pwd:
                        print("\n[LOGIN SUCCESS] Login successful.\n")
                        logger.info(f"[LOGIN SUCCESS] UserID: {userid}")
                        client_socket.send("Password Match".encode("utf-8"))
                        count = 0
                        while restart:
                            print(
                                "\n1. Upload\n"
                                "2. Download\n"
                                "3. Preview (First 1024 bytes only)\n"
                                "4. Delete File\n"
                                "5. List Directory\n"
                                "6. Exit\n"
                            )
                            choice = input("Enter your choice: ")
                            client_socket.send(choice.encode('utf-8'))

                            try:
                                timeout_message = client_socket.recv(1024).decode('utf-8')
                                if timeout_message == "TIMEOUT":
                                    print("\n[TIMEOUT] You have been logged out due to inactivity.\n")
                                    break
                                
                                if choice == '1':
                                    file_name = input("\nEnter the file location (or type 'exit' to cancel upload): ")
                                    if file_name.lower() == 'exit':
                                        print("\n[INFO] Canceled the upload.\n")
                                        break
                                    count += 1
                                    upload_file(client_socket, file_name, count)
                                    logger.info(f"File uploaded: {file_name}")
                                elif choice == '2':
                                    response = client_socket.recv(4096).decode('utf-8')
                                    print(f"\n{response}\n")
                                    file_name = input("Enter the file name to download: ")
                                    download_dir = input("Enter the directory to save the file: ")
                                    download_file(client_socket, file_name, download_dir, userid)
                                    logger.info(f"File downloaded: {file_name}")
                                elif choice == '3':
                                    response = client_socket.recv(4096).decode('utf-8')
                                    print(f"\n{response}\n")
                                    file_name = input("Enter the file name to preview: ")
                                    preview_file(client_socket, file_name, userid)
                                elif choice == '4':
                                    print("\n[INFO] Directory listing:\n")
                                    response = client_socket.recv(4096).decode('utf-8')
                                    if response == "No files available.":
                                        print(f"\n{response}\n")
                                        continue
                                    print(f"\n{response}\n")
                                    logger.info("Directory listed")

                                    file_name = input("Enter the name of the file to delete: ")
                                    client_socket.send(file_name.encode('utf-8'))
                                    response = client_socket.recv(1024).decode('utf-8')
                                    print(f"\n{response}\n")
                                    logger.info(f"File deleted: {file_name}")
                                elif choice == '5':
                                    print("\n[INFO] Directory listing:\n")
                                    response = client_socket.recv(4096).decode('utf-8')
                                    print(f"\n{response}\n")
                                    logger.info("Directory listed")
                                elif choice == '6':
                                    print("\n[INFO] Exiting the client.\n")
                                    logger.info("Exiting the client.")
                                    restart = False
                                else:
                                    print("\n[ERROR] Invalid choice. Please select from 1 to 6.\n")
                                    logger.warning(f"Invalid choice: {choice}")
                            except (ConnectionAbortedError, ConnectionResetError):
                                print("\n[ERROR] Connection to the server was lost.\n")
                                break
                    else:
                        print("\n[LOGIN FAILED] Password does not match.\n")
                        logger.warning(f"[LOGIN FAILED] Incorrect password for UserID: {userid}.")
                else:
                    print("\n[LOGIN FAILED] User not found.\n")
            else:
                print("\n[ERROR] Handshake failed.\n")
                logger.error("Handshake failed.")
        except (ConnectionAbortedError, ConnectionResetError) as e:
            print(f"\n[ERROR] Connection error: {str(e)}\n")
            logger.error(f"[ERROR] {str(e)}")
        finally:
            client_socket.close()
            logger.info("Client socket closed.")

if __name__ == "__main__":
    main()
