import socket

def scan_ports(ip_address, start_port, end_port):
    open_ports = []

    for port in range(start_port, end_port + 1):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.1)
        if s.connect_ex((ip_address, port)) == 0:
            open_ports.append(port)
        s.close()
    print(f"Доступные порты для {ip_address}:", open_ports)

scan_ports("127.0.0.1", 1, 10000)
