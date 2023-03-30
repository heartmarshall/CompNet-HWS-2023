# python3
import os
import socket
import click
import threading
import subprocess
import logging
import time

LOCAL_STORAGE_PATH = os.path.join(os.getcwd(), 'localfiles')



class Server():
    def __init__(self, host, port, conc_level):
        self.port = port
        self.conc_level = conc_level
        self.host = host


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
        request = self.read_request(client_sock)
        print("REQUEST:", request)
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
        program_call = request.split()
        prog_name = program_call[0]

        try:
            proc = subprocess.Popen(program_call, stdout=subprocess.PIPE)
        except FileNotFoundError:
            return f"Error: {prog_name} not found"

        response_body = ""
        start_time = time.monotonic()
        time_limit = 30.0

        while True:
            try:
                output = proc.stdout.readline()
            except subprocess.TimeoutExpired:
                if time.monotonic() - start_time >= time_limit:
                    response_body += "EXIT: process execution time exceeded."
                    proc.kill()
                    break
            else:
                if not output:
                    break
                response_body += output.decode("utf-8")
        proc.kill()
        return response_body

    def write_response(self, client_sock, response):
        client_sock.sendall(response)
        client_sock.close()
        print(f'Client #{self.cid} has been served')


@click.command()
@click.argument('host', required=False, default="127.0.0.1")
@click.argument('port', required=False, default=8008)
@click.option('conc_level', '-c', '--concurrencyLevel', required=False, default=10, type=int)
def main(host, port, conc_level):
    server = Server(host, port, conc_level)
    server.run_server()
    

if __name__ == "__main__":
    main()