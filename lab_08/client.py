import socket
import time
import click
import os
import random

LOCAL_STORAGE_PATH = os.path.join(os.getcwd(), 'localfiles')


def package_has_lost(lost_chanse=3):
    return random.randint(0, 10) < lost_chanse


def str_to_chunks(data: str, chunk_size=1024):
    if chunk_size <= 0:
        raise ValueError("Длина чанка не может быть меньше 1")
    chunk_size = min(chunk_size, len(data))
    chunks = []
    for pos in range(0, len(data),  chunk_size):
        chunks.append(data[pos:pos+chunk_size])
    # chunks = [data[pos: pos + chunk_size] for pos in range(0, len(data) - chunk_size + 1)]
    return chunks



@click.command()
@click.argument('server_ip', required=True, default="127.0.0.1")
@click.argument('server_port', required=True, default=8008, type=int)
@click.argument('client_ip', required=False, default="127.0.0.1")
@click.argument('client_port', required=False, default=8009, type=int)
@click.option('file_path', "-f", required=False, default="send.txt", type=str)
@click.option('buff_size', "-bf", required=False, default=16, type=int)
@click.option('timeout', "-t", required=False, default=1, type=int)
def run_client(server_ip, server_port, client_ip, client_port, file_path, buff_size, timeout):
    start_time = time.time()
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    client_sock.bind((client_ip, client_port))
    client_sock.settimeout(timeout)

    if os.path.isfile(os.path.join(LOCAL_STORAGE_PATH, file_path)):
        file_path = os.path.join(LOCAL_STORAGE_PATH, file_path)

    f = open(file_path, "rb")
    chunks = str_to_chunks(f.read(), buff_size-1)
    f.close()

    ack_num = 0
    losted_count = 0
    for chunk_num, chunk in enumerate(chunks):
        while True:
            print(f"pkg:{chunk_num}:ack:{ack_num}: попытка отправить пакет") # TODO: надо бы вынести  pkg:{chunk_num}:ack:{chunk_num}: в отдельную переменную
            if package_has_lost():
                print(f"pkg:{chunk_num}:ack:{ack_num}: пакет утерян !!!")
                time.sleep(2)
                losted_count += 1
                continue

            if chunk_num == len(chunks) - 1:
                ack_num = 2

            try:
                send_datagram(client_sock, server_ip, server_port, ack_num, chunk)
                print(f"pkg:{chunk_num}:ack:{ack_num}: пакет отправлен")
                response = receive_response(client_sock, buff_size)
                response_ack_num = int(response[0])

                if (response_ack_num != ack_num):
                    print(f"pkg:{chunk_num}:ack:{ack_num}: несовпадение ACK")
                    continue

                print(f"pkg:{chunk_num}:ack:{ack_num}: пакет передан успешно")
                ack_num = 1 - ack_num
                break

            except socket.timeout:
                print(f"pkg:{chunk_num}:ack:{ack_num}: TIMEOUT: сервер не ответил подтверждением. Запущена повторная отправка пакета")

    print(f"Передача файла закончена\n"
          f"Затрачено времени: {time.time() - start_time:.5f} сек.\n"
          f"Утеряно пакетов: {losted_count} из {chunk_num+1+losted_count}\n")

def send_datagram(client_sock, server_ip, server_port, ack_num, data):
    datagram = ack_num.to_bytes(1, "big") + data
    client_sock.sendto(datagram, (server_ip, server_port))


def receive_response(client_sock, buff_size=1024):
    response = bytearray()
    try:
        while True:
            chunk = client_sock.recv(buff_size)
            response += chunk
            if len(chunk) < buff_size:
                return response
    except ConnectionResetError:
        # Соединение было неожиданно разорвано.
        return None


if __name__ == '__main__':
    run_client()
