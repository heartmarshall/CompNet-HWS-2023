# python3
import os
import socket
import click
import threading
import logging
from logging import StreamHandler, Formatter

LOCAL_STORAGE_PATH = os.path.join(os.getcwd(), 'localfiles')



class Proxy_server():
    def __init__(self, host, port, conc_level, log_file, blacklist_filename):
        self.port = port
        self.conc_level = conc_level
        self.host = host
        logging.basicConfig(filename=log_file, level=logging.INFO, format='[%(asctime)s: %(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        self.blacklist = self.read_blacklist(blacklist_filename)


    def read_blacklist(self, blacklist_filename):
        with open(blacklist_filename, 'r') as f:
            sites = f.readlines()
            return set([s.rstrip() for s in sites])

    def run_server(self):
        self.serv_sock = self.create_serv_sock() # TODO: поставить обработку ошибки занятого порта.
        self.semaphore = threading.Semaphore(self.conc_level)
        self.cid = 0 # TODO: скорее всего есть траблы с этим параметром - он затирается из-за многопоточности
        while True:
            client_sock = self.accept_client_conn()
            self.serve_client(client_sock, self.cid, self.semaphore)
            # self.semaphore.acquire()
            # t = threading.Thread(target=self.serve_client,
            #                     args=(client_sock, self.cid, self.semaphore))
            # t.start()
            self.cid += 1

    def create_serv_sock(self):
        """
        Создаёт сокет и сразу переводит его в режим ожидания запроса. 
        """
        serv_sock = socket.socket(socket.AF_INET,
                                socket.SOCK_STREAM)
        serv_sock.bind((self.host, self.port))
        serv_sock.listen(100)
        print(f"Listening on port {self.port}...")
        return serv_sock
    
    def accept_client_conn(self):
        client_sock, client_addr = self.serv_sock.accept()
        print(f'Client #{self.cid} connected {client_addr[0]}:{client_addr[1]}')
        return client_sock
    
    def serve_client(self, client_sock, cid, semaphore):
        """
        Считывает запрос клиента, обрабатывает его и отправляет клиенту ответ.
        """
        request = self.read_request(client_sock) # считываем запрос клиента, узнаём куда он хочет обратиться
        if request is None:
            print(f'Client #{cid} unexpectedly disconnected')
        else:
            response = self.handle_request(request)
            self.write_response(client_sock, response.encode())
        # semaphore.release()

    def read_request(self, client_sock, N=4096, timeout=30):
        """
        Считывает весь запрос клиента чанками по N байт.
        """
        request = bytearray()
        try:
            client_sock.settimeout(timeout)
            while True:
                chunk = client_sock.recv(N)
                request += chunk
                if len(chunk) < N:
                    break
        except (ConnectionResetError, TimeoutError, socket.timeout):
            return None
        finally:
            client_sock.settimeout(None)
        return request.decode()

    def handle_request(self, request):
        method, url, protocol = request.split('\r\n')[0].split() #

        if '/' in url[1:]:
            host, requested_url = url[1:].split('/', 1)
        else:
            host = url[1:]
            requested_url = ""

        if host in self.blacklist:
            logging.info(f"{method} {url}: 403")
            return "403 This page is blocked"

        web_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            web_socket.connect((host, 80))
        except socket.gaierror:
            logging.info(f"{method} {url}: 523")
            return "523 name or service not known"
        
        body = ""
        if method == "POST":
            body = request.split("\r\n\r\n", 1)[1]

        web_socket.sendall(f'{method} /{requested_url} {protocol}\r\nHost: {host}\r\n\r\n{body}'.encode())
        response = self.read_request(web_socket)

        if response is not None:
            status_code = response.split("\r\n", 1)[0].split(" ", 1)[1]
            logging.info(f"{method} {url}: {status_code}")
        else:
            logging.info(f"{method} {url}: 522")
            response = "522 connection Timed Out"

        return response
    
    def write_response(self, client_sock, response):
        client_sock.sendall(response)
        client_sock.close()
        print(f'Client #{self.cid} has been served')


@click.command()
@click.argument('host', required=False, default="127.0.0.1")
@click.argument('port', required=False, default=8008)
@click.option('conc_level', '-c', '--concurrencyLevel', required=False, default=10, type=int)
@click.option('logfile', '-l', '--logfile', required=False, default="log.txt", type=str)
@click.option('blacklist_filename', '-b', '--blacklist', required=False, default="blacklist.txt", type=str)
def main(host, port, conc_level, logfile, blacklist_filename):
    proxy = Proxy_server(host, port, conc_level, logfile, blacklist_filename)
    proxy.run_server()
    

if __name__ == "__main__":
    main()