import socket

# Создаем объект сокета
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Получаем информацию об интерфейсе с помощью метода getsockname()
s.connect(('8.8.8.8', 80))
ip_address = s.getsockname()[0]
s.close()

# Выводим IP-адрес и маску сети на консоль
print(f"IP-адрес: {ip_address}")

# Получаем маску сети
subnet_mask = socket.inet_ntoa(socket.inet_aton(ip_address)[::-1].lstrip(b'\xff'))
print(f"Маска сети: {subnet_mask}")
