# python3

import socket
import click
import os

LOCAL_STORAGE_PATH = os.path.join(os.getcwd(), 'localfiles')


@click.command()
@click.argument('ip', required=False, default="127.0.0.1")
@click.argument('port', required=False, default=8008)
@click.argument('programm_call', required=True)
def run_client(ip, port, programm_call):
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    rid = 0
    client_sock.connect((ip, port))

    while True:
        request = programm_call
        send_request(client_sock, request)
        response = read_response(client_sock)
        print(response.decode("UTF-8"))



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

if __name__ == '__main__':
    run_client()
