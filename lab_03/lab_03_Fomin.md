# Практика 3. Прикладной уровень
## Выполнил Никита Фомин Б-06

### Программирование сокетов. Веб-сервер 

### А. Однопоточный веб-сервер 

Сервер написан на python, с использованием библиотеки `socket`. Вот получившийся код:

```py
import socket
import os

HOST = "127.0.0.1"
PORT = 8008
LOCAL_STORAGE_PATH = os.path.join(os.getcwd(), 'localfiles')

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1) 
print('Listening on port 8008..')

while True:
    client_socket, address = server_socket.accept()
    request = client_socket.recv(1024).decode()

    requested_file_path = os.path.join(LOCAL_STORAGE_PATH, request.split()[1][1:]) 

    if os.path.exists(os.path.join(requested_file_path)):
        with open(requested_file_path, 'rb') as file:
            file_content = file.read()
        response = 'HTTP/1.1 200 OK\n\n'.encode() + file_content
    else:
        response = 'HTTP/1.1 404 Not Found\n\nFile not found'

    client_socket.sendall(response)
    client_socket.close()
    print(f"user {address[0]} was served")

```

Файлы, которые могут быть возвращены пользователю, лежат в дирректории `./server/localfiles/`. Для тестировки туда помещены несколько картинок, txt и html документы.

Попробуем запросить у сервера картинку, запустив наш сервер и введя в браузере запрос:

Запуск сервера:
```
$ python3 server.py                                                                                     
Listening on port 8008..
```
Запрос в браузере:
```
http://127.0.0.1:8008/earth.jpg
```
Результат:
![image](./pics/1.png)

### Многопоточный веб-сервер
