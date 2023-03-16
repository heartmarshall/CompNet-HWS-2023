# python3
import os
import socket
import sys
import time
import click
import threading

from collections import deque

LOCAL_STORAGE_PATH = os.path.join(os.getcwd(), 'localfiles')


@click.command()
@click.argument('port', required=False, default=8008)
@click.option('conc_level', '-c', '--concurrencyLevel', required=False, default=10, type=int)
def run_server(port, conc_level):
    serv_sock = create_serv_sock(port)
    semaphore = threading.Semaphore(conc_level)
    cid = 0
    while True:
        client_sock = accept_client_conn(serv_sock, cid)
        semaphore.acquire()
        t = threading.Thread(target=serve_client,
                             args=(client_sock, cid, semaphore))
        t.start()
        cid += 1


def serve_client(client_sock, cid, semaphore):
    """
    Считывает запрос клиента, обрабатывает его и отправляет клиенту ответ.
    """
    request = read_request(client_sock)
    if request is None:
        print(f'Client #{cid} unexpectedly disconnected')
    else:
        response = handle_request(request)
        write_response(client_sock, response, cid)
    semaphore.release()


def create_serv_sock(serv_port, host_address="127.0.0.1"):
    """
    Создаёт сокет и сразу переводит его в режим ожидания запроса. 
    """
    serv_sock = socket.socket(socket.AF_INET,
                              socket.SOCK_STREAM)
    serv_sock.bind((host_address, serv_port))
    serv_sock.listen(100)
    print(f"Listening on port {serv_port}...")
    return serv_sock


def accept_client_conn(serv_sock, cid):
    """
    Блокирует выполнение до следующего подключения клиента. Затем считывает его запрос и возвращает сокет клиента. 
    """
    client_sock, client_addr = serv_sock.accept()
    print(f'Client #{cid} connected '
          f'{client_addr[0]}:{client_addr[1]}')
    return client_sock


# Можно добавить разделитель, после которого считывание прекращается.
def read_request(client_sock):
    """
    Считывает весь запрос клиента чанками по 4 байта.
    """
    request = bytearray()
    try:
        while True:
            chunk = client_sock.recv(4)
            if len(chunk) < 4:
                return request.decode()
            request += chunk
    except ConnectionResetError:
        # Соединение было неожиданно разорвано.
        return None
    except:
        raise


def handle_request(request):
    print("-------------------------------------")
    print(request)
    requested_file_path = os.path.join(
        LOCAL_STORAGE_PATH, request.split()[1][1:])
    if os.path.exists(os.path.join(requested_file_path)):
        with open(requested_file_path, 'rb') as file:
            file_content = file.read()
            response = 'HTTP/1.1 200 OK\r\n\r\n'.encode() + file_content
    else:
        response = b'HTTP/1.1 404 Not Found\r\n\r\nFile not found'
    return response


def write_response(client_sock, response, cid):
    client_sock.sendall(response)
    client_sock.close()
    print(f'Client #{cid} has been served')


if __name__ == '__main__':
    run_server()
