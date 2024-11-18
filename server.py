import socket
import os
from concurrent.futures import ThreadPoolExecutor
from file_upload import recv_file
from file_download import send_file
from file_preview import read_file
from file_delete import delete_file
from threading import Semaphore
import signal
import sys
import time
import logging
from logger_util import setup_logger

logger = setup_logger("ServerLogger", "logs/server.log")

TIMEOUT_DURATION = 100 

MAX_CONCURRENT_CLIENTS = 2
semaphore = Semaphore(MAX_CONCURRENT_CLIENTS)

def signal_handler(sig, frame):
    print("\n[SERVER SHUTDOWN] Signal received, closing server socket...")
    server_socket.close()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def validate_file_path(user_dir, file_path):
    abs_path = os.path.abspath(os.path.join(user_dir, file_path))
    path = abs_path.strip().split("\\")
    user = user_dir.strip().split("\\")
    if user[1] not in path :
        raise ValueError(f"Invalid file path, outside of user's directory. {file_path} is not allowed.")
    
    return abs_path



def handle_client(client_socket, addr):
    logger.info(f"[NEW CONNECTION] {addr} connected.")
    if not semaphore.acquire(blocking=False):
        logger.warning(f"[SERVER BUSY] Too many connections. Rejected {addr}.")
        client_socket.send("Please wait, the server is busy.".encode('utf-8'))
        semaphore.acquire()  

    client_socket.send("You are now connected to the server.".encode('utf-8'))
    print(f"[NEW CONNECTION] {addr} connected.")
    logger.debug(f"[WELCOME MESSAGE SENT] To {addr}.")
    last_active_time = time.time()
    try:
        message = client_socket.recv(1024).decode('utf-8')
        if message == "HELLO":
            logger.debug(f"Received handshake from {addr}.")
            client_socket.send("ACK".encode('utf-8'))
            userid = client_socket.recv(1024).decode('utf-8')
            logger.info(f"[USER LOGIN ATTEMPT] UserID: {userid}")
            user_dir = os.path.join("server_storage", userid)
            os.makedirs(user_dir, exist_ok=True)
            last_active_time = time.time()

            credentials = {}
            if os.path.exists("id_passwd.txt"):
                with open("id_passwd.txt", "r") as file:
                    credentials = dict(line.strip().split(":") for line in file)
                    
            correct_pwd = credentials.get(userid, "")

            client_socket.send(f"Password:{correct_pwd}".encode('utf-8'))
            response = client_socket.recv(1024).decode('utf-8')
            last_active_time = time.time()

            if response == "Password Match":
                logger.info(f"[LOGIN SUCCESS] User {userid} logged in.")
                user_dir = os.path.join("server_storage", userid)
                os.makedirs(user_dir, exist_ok=True)

                while True:
                    client_socket.settimeout(TIMEOUT_DURATION)
                    try:
                        choice = client_socket.recv(1024).decode('utf-8')
                        logger.debug(f"[REQUEST RECEIVED] Choice: {choice} from {addr}.")
                        last_active_time = time.time()
                        client_socket.settimeout(None)

                        if time.time() - last_active_time > TIMEOUT_DURATION:
                            print(f"[TIMEOUT] {addr} inactive for {TIMEOUT_DURATION} seconds. Disconnecting...")
                            logger.warning(f"[TIMEOUT] {addr} inactive for {TIMEOUT_DURATION} seconds.")
                            client_socket.send("TIMEOUT".encode('utf-8'))
                            break
                        else:
                            client_socket.send("PROCEED".encode('utf-8'))
                        if choice == '1':
                            print(f"[UPLOAD REQUEST] Receiving file from {addr}")
                            logger.info(f"[UPLOAD REQUEST] Receiving file from {addr}.")
                            recv_file(client_socket, user_dir)
                        elif choice == '2':
                            files = os.listdir(user_dir)
                            files_list = "\n".join(files) if files else "No files available."
                            client_socket.send(files_list.encode('utf-8'))
                            print(f"[LIST] Directory listing sent to {addr}")

                            file_path = client_socket.recv(1024).decode('utf-8')
                            print(f"[DOWNLOAD REQUEST] Received file path: {file_path}")


                            if not file_path.startswith(f"./server_storage/{userid}/"):
                                client_socket.send(struct.pack("Q", 0)) 
                                print(f"[ERROR] Unauthorized access attempt by {addr}.")
                                logger.error(f"[ERROR] Unauthorized access attempt by {addr}.")
                                return

                            if os.path.isfile(file_path):
                                send_file(client_socket, file_path)
                                print(f"[DOWNLOAD REQUEST] Sent file '{file_path}' to {addr}")
                                logger.info(f"[DOWNLOAD REQUEST] Sent file '{file_path}' to {addr}.")
                            else:
                                client_socket.send(struct.pack("Q", 0)) 
                                print(f"[ERROR] File '{file_path}' not found.")
                                logger.error(f"[ERROR] File '{file_path}' not found.")

                        elif choice == '3':
                            file_path = client_socket.recv(1024).decode('utf-8') 
                            try:
                                validated_path = validate_file_path(user_dir, file_path) 
                                logger.info(f"[PREVIEW REQUEST] Sending preview of {file_path} to {addr}.")
                                print(f"[PREVIEW REQUEST] Sending file {file_path} to {addr}")
                                read_file(client_socket, validated_path)  
                            except ValueError as e:
                                client_socket.send(f"Error: {e}".encode('utf-8'))
                                logger.error(f"[INVALID FILE PATH] {e}")
                        elif choice =='4':
                            files = os.listdir(user_dir)
                            files_list = "\n".join(files) if files else "No files available."
                            client_socket.send(files_list.encode('utf-8'))
                            print(f"[LIST] Directory listing sent to {addr}")
                            logger.info(f"[LIST REQUEST] Sent directory listing to {addr}.")

                            file_name = client_socket.recv(1024).decode('utf-8')
                            response = delete_file(user_dir, file_name)  
                            client_socket.send(response.encode('utf-8'))
                            logger.info(f"[DELETE REQUEST] {response} by {addr}.")
                            print(f"[DELETE] {response} by {addr}")
                        elif choice =='5':
                            files = os.listdir(user_dir)
                            files_list = "\n".join(files) if files else "No files available."
                            client_socket.send(files_list.encode('utf-8'))
                            print(f"[LIST] Directory listing sent to {addr}")
                            logger.info(f"[LIST REQUEST] Sent directory listing to {addr}.")
                        elif choice == '6':
                            print(f"[CLIENT EXIT] {addr} requested to exit.")
                            logger.info(f"[CLIENT EXIT] {addr} requested to exit.")
                            break
                        else:
                            print(f"[ERROR] Unhandled choice: {choice}")
                            logger.warning(f"[INVALID REQUEST] {choice} from {addr}.")
                    except socket.timeout:
                        print(f"[TIMEOUT] {addr} inactive for {TIMEOUT_DURATION} seconds. Disconnecting...")
                        logger.warning(f"[TIMEOUT] {addr} inactive for {TIMEOUT_DURATION} seconds.")
                        client_socket.send("TIMEOUT".encode('utf-8'))
                        break
            else:
                print(f"[LOGIN FAILED] Incorrect password for {userid}")
                logger.warning(f"[LOGIN FAILED] Incorrect password for UserID: {userid}.")
        else:
            print(f"[ERROR] Invalid handshake from client {addr}")
            logger.error(f"[HANDSHAKE FAILED] Invalid message from {addr}.")
    finally:
        client_socket.close()
        print(f"[DISCONNECTED] {addr} disconnected.")
        logger.info(f"[DISCONNECTED] {addr} disconnected.")
        semaphore.release()  

def start_server():
    global server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('127.0.0.1', 8888))
    server_socket.listen()
    print("[SERVER STARTED] Listening on port 8888.")
    logger.info("[SERVER STARTED] Listening on port 8888.")

    with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_CLIENTS) as executor:
        while True:
            client_socket, addr = server_socket.accept()
            print(f"[CONNECTION ACCEPTED] Connection from {addr}")
            logger.info(f"[CONNECTION ACCEPTED] Connection from {addr}.")
            executor.submit(handle_client, client_socket, addr)


if __name__ == "__main__":
    start_server()
