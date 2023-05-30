import os
import socket
import click
import logging
import random

LOCAL_STORAGE_PATH = os.path.join(os.getcwd(), 'localfiles')

def package_has_lost(lost_chanse=0.3):
    return random.uniform(0, 1) <= lost_chanse


class Server():
    def __init__(self, host, port, file_path, buff_size=16):
        self.port = port
        self.host = host
        self.file_path = file_path
        self.buff_size = buff_size

    def send_datagram(self, addres, ack_num):
        datagram = ack_num.to_bytes(1, "big") 
        self.serv_sock.sendto(datagram, addres)

    def run_server(self):
        self.serv_sock = self.create_serv_sock()
        f = open(self.file_path, "wb")
        while True:
            data, adress = self.serv_sock.recvfrom(self.buff_size)
            if package_has_lost():
                print("PACKAGE HAS LOST")
                continue
            ack_num = int(data[0])
            data = data[1:]
            print(f"Получен пакет с ACK {ack_num}")
            f.write(data)
            print(f"Отправлено подтверждение с ACK{ack_num}")
            self.send_datagram(adress, ack_num)
            if ack_num == 2:
                    break
                
        f.close()
        print(f"Файл {self.file_path} записан")

    def create_serv_sock(self):
        """
        Создаёт сокет и сразу переводит его в режим ожидания запроса. 
        """
        serv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        serv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serv_sock.bind((self.host, self.port))
        print(f"Listening on port {self.port}...")
        return serv_sock


@click.command()
@click.argument('host', required=False, default="127.0.0.1", type=str)
@click.argument('port', required=False, default=8008, type=int)
@click.option('file_path', "-f", required=False, default="recv.txt", type=str)
@click.option('buff_size', "-bf", required=False, default=16, type=int)
def main(host, port, file_path, buff_size):
    server = Server(host, port, file_path, buff_size)
    server.run_server()
if __name__ == "__main__":
    main()
