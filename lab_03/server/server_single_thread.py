import socket
import os

HOST = "127.0.0.1"
PORT = 8000
LOCAL_STORAGE_PATH = os.path.join(os.getcwd(), 'localfiles')

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

print('Listening on port 8008..')

while True:
    client_socket, address = server_socket.accept()

    request = client_socket.recv(1024).decode()
    print(request)
    requested_file_path = os.path.join(
        LOCAL_STORAGE_PATH, request.split()[1][1:])

    if os.path.exists(os.path.join(requested_file_path)):
        with open(requested_file_path, 'rb') as file:
            file_content = file.read()
        response = 'HTTP/1.1 200 OK\n\n'.encode() + file_content
    else:
        response = b'HTTP/1.1 404 Not Found\n\nFile not found'

    client_socket.send(response)
    client_socket.close()
    print(f"user {address[0]} was served")
