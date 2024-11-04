import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('127.0.0.1', 12345))

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

        while True:
            print("1.Upload\t2.Download\t3.View\t4.Delete\t5.List\t6.Exit : ")
            choice = input("Enter your choice:")
            if choice == '1':
                # upload()
                client_socket.send(choice.encode('utf-8'))
                pass
            elif choice == '2':
                client_socket.send(choice.encode('utf-8'))
                pass
            elif choice == '3':
                client_socket.send(choice.encode('utf-8'))
                pass
            elif choice == '4':
                client_socket.send(choice.encode('utf-8'))
                pass
            elif choice == '5':
                client_socket.send(choice.encode('utf-8'))
                pass
            elif choice == '6':
                client_socket.send(choice.encode('utf-8'))
                break
            else:
                print("Wrong choice. Please try again!")
    else:
            print("Not matched")
else:
    print("Handshake failed")

client_socket.close()

