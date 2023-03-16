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
    rid = 0
    client_sock.connect((ip, port))

    while True:
        save_file_from_server(client_sock, file_name, download_dir, rid)
        exit()
        # TODO: сделать так, чтобы можно было отправлять несколько запросов подряд
        # print("Enter new file name or exit() to stop client...") # Не получается скачать новый файл - выдаёт ошибку
        # file_name = input()
        # if file_name == "exit()":
        #     client_sock.close()
        #     exit()
        # rid += 1


def send_request(client_sock, request):
    client_sock.sendall(request.encode())


def read_response(client_sock):
    response = bytearray()
    try:
        while True:
            chunk = client_sock.recv(1024)
            response += chunk
            if len(chunk) < 1024:
                return response
    except ConnectionResetError:
        # Соединение было неожиданно разорвано.
        return None


def save_file_from_server(client_sock, file_name, download_dir="", rid=None):
    request = f"GET /{file_name} HTTP/1.1\r\n"
    send_request(client_sock, request)
    print(f"Request #{rid} sended")
    response_headers, response_body = read_response(client_sock).split(b'\r\n\r\n', 1)

    if response_headers.split(b' ')[1] == b'404':
        print("File not founded")
        return 1
    
    if not download_dir:
        download_dir = os.getcwd()
    with open(os.path.join(download_dir, file_name), "wb") as f:
        f.write(response_body)
        print(f"File from request #{rid} saved!")


if __name__ == '__main__':
    run_client()
