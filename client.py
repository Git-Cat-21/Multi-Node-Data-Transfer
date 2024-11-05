import socket
import os

def upload_file():
    count = 0
    while True:
        count += 1
        file_name = input("Enter the file location (or type 'exit' to quit): ")
        if file_name.lower() == 'exit':
            print("Exiting the client.")
            break

        file_size = os.path.getsize(file_name)
        file_ext = input("Enter the extension of the file: ")
        recv_file_name = "received_file" + str(count) + file_ext

        client_socket.send(recv_file_name.encode())
        client_socket.send(str(file_size).encode())

        with open(file_name, "rb") as file:
            while (data := file.read(1024)):
                client_socket.send(data)

        client_socket.send(b"<END>")
        print(f"{file_name} has been sent successfully.")

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('127.0.0.1', 8888))

# Initial handshake
client_socket.send("HELLO".encode('utf-8'))
response = client_socket.recv(1024).decode('utf-8')
if response == "ACK":
    print("Handshake successful")
    userid = input("Username: ")
    pwd = input("Password: ")

    client_socket.send(userid.encode('utf-8'))
    response = client_socket.recv(1024).decode('utf-8')
    pwd_check = response.split(":")

    if pwd_check[1].strip() == pwd.strip():
        print("Login successful")
        client_socket.send("Password Match".encode("utf-8"))

        while True:
            print("1.Upload\t2.Download\t3.View\t4.Delete\t5.List\t6.Exit : ")
            choice = input("Enter your choice:")
            if choice == '1':
                client_socket.send(choice.encode('utf-8'))
                upload_file()
            elif choice == '2':
                client_socket.send(choice.encode('utf-8'))
            elif choice == '3':
                client_socket.send(choice.encode('utf-8'))
            elif choice == '4':
                client_socket.send(choice.encode('utf-8'))
            elif choice == '5':
                client_socket.send(choice.encode('utf-8'))
            elif choice == '6':
                    break
            else:
                print("Wrong choice. Please try again!")
    else:
        print("Login failed: Password does not match.")
else:
    print("Handshake failed")

client_socket.close()
