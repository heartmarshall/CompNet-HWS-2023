# python3

import socket
import click
import os

LOCAL_STORAGE_PATH = os.path.join(os.getcwd(), 'localfiles')


@click.command()
@click.argument('ip', required=False, default="127.0.0.1")
@click.argument('port', required=False, default=8008)
@click.argument('file_name', required=True)
@click.option('-d', 'download_dir', default="")
def run_client(file_name, ip, port, download_dir):
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_sock.connect((ip, port))
    rid = 0
    while True:
        save_file_from_server(client_sock, file_name, download_dir, rid)
        print("Enter new file name or exit() to stop client")
        file_name = input()
        if file_name == "exit()":
            exit()
        rid += 1


def send_request(client_sock, request):
    client_sock.sendall(request.encode())


def read_response(client_sock):
    response = bytearray()
    try:
        while True:
            chunk = client_sock.recv(4)
            response += chunk
            if len(chunk) < 4:
                return response.decode()
    except ConnectionResetError:
        # Соединение было неожиданно разорвано.
        return None


def save_file_from_server(client_sock, file_name, download_dir="", rid=None):
    request = f"GET /{file_name} HTTP/1.1\r\n"
    send_request(client_sock, request)
    print(f"Request #{rid} sended")
    response_headers, response_body = read_response(client_sock).split('\r\n\r\n', 1)
    if not download_dir:
        download_dir = os.getcwd()
    with open(os.path.join(download_dir, file_name), "wb") as f:
        f.write(response_body.encode())


if __name__ == '__main__':
    run_client()