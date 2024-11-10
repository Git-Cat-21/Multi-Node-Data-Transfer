import socket
import os
import struct
import signal
import sys
import threading
import time

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

signal.signal(signal.SIGINT, signal_handler)

def main():
    global client_socket, session_expired
    while True:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('127.0.0.1', 8888))

        try:
            client_socket.send("HELLO".encode('utf-8'))
            response = client_socket.recv(1024).decode('utf-8')

            if response == "ACK":
                while True:
                    if session_expired:
                        print("\n[SESSION EXPIRED] Please log in again.")
                        session_expired = False  # Reset session expiration flag
                    
                    userid = input("Username: ")
                    pwd = input("Password: ")

                    client_socket.send(userid.encode('utf-8'))
                    password_response = client_socket.recv(1024).decode('utf-8')
                    correct_pwd = password_response.split(":")[1].strip()

                    if pwd == correct_pwd:
                        print("Login successful.")
                        client_socket.send("Password Match".encode("utf-8"))

                        # Start inactivity timeout thread
                        timeout_thread = threading.Thread(target=post_login_timeout)
                        timeout_thread.start()
                        
                        while True:
                            print("1.Upload\t2.Download\t3.View\t4.Delete\t5.List\t6.Exit : ")
                            choice = input("Enter your choice: ")
                            reset_timeout()  # Reset timer upon any action
                            
                            client_socket.send(choice.encode('utf-8'))

                            if choice == '1':
                                upload_file(client_socket)
                            elif choice == '6':
                                print("Exiting the client.")
                                session_expired = True  # Mark session as expired to require re-login
                                break
                            else:
                                print("Functionality for this option is not implemented yet.")
                        
                        timeout_thread.join()  # Wait for the timeout thread to finish
                        break  # Break out to re-login if session expires or user exits

                    else:
                        print("Login failed: Password does not match.")
            else:
                print("Handshake failed.")
        finally:
            client_socket.close()
            if input("Do you want to try logging in again? (y/n): ").lower() != 'y':
                break

def post_login_timeout():
    global last_active_time, client_socket, session_expired
    while True:
        if time.time() - last_active_time > 10:
            print("\n[SESSION EXPIRED] Due to inactivity. Please log in again.")
            client_socket.close()
            session_expired = True  # Flag session as expired to prompt re-login
            break
        time.sleep(1)

def reset_timeout():
    global last_active_time
    last_active_time = time.time()

if __name__ == "__main__":
    last_active_time = time.time()  # Initialize the last active time
    session_expired = False  # Initialize session expiration flag
    main()