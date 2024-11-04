import socket


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('127.0.0.1', 12345))

# Initial handshake
client_socket.send("HELLO".encode('utf-8'))
response = client_socket.recv(1024).decode('utf-8')
if response == "ACK":
    print("Handshake successful")

    while True:
        userid = input("Username: ")
        pwd = input("Password: ")

        client_socket.send(userid.encode('utf-8'))
        response = client_socket.recv(1024).decode('utf-8')
        pwd_check = response.split(":")

        if pwd_check[1].strip() == pwd.strip():
            print("1.Upload\t2.Download\t3.View\4.Delete\5.List\6.Exit : ")
            choice = int(input("Enter your choice:"))
            if choice == 1:
                # upload()
                pass
            elif choice == 2:
                pass
            elif choice == 3:
                pass
            elif choice == 4:
                pass
            elif choice == 5:
                pass
            elif choice == 6:
                break
        
            else:
                print("Wrong choice. Please try again!")
        else:
            print("Not matched")
        if userid.lower() == "exit":
            break
else:
    print("Handshake failed")

client_socket.close()

