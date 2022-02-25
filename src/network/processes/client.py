from socket import socket

sock = socket()
sock.connect(('localhost', 5555))

name = input("Name: ")
while command := input("> ").lower():
    if command == "read":
        sock.sendall(name.encode())
        print(sock.recv(4096).decode())
    elif command == "change name":
        name = input("Name: ")
    else:
        print("Invalid command")
