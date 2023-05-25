import time
import psutil

DELAY = 1


def get_size(bytes):
    power_lables = ["", "K", "M", "G", "T", "P", "Z"]
    power = 1024
    i = 0
    while bytes > power:
        bytes /= 1024
        i += 1
    return f"{bytes:.2f}{power_lables[i]}"

# Инициализируем начальные значения
start_network_scan = psutil.net_io_counters()
bytes_sent, bytes_recv = start_network_scan.bytes_sent, start_network_scan.bytes_recv
start_download, start_upload = start_network_scan.bytes_recv, start_network_scan.bytes_sent

while True:
    # get the stats again
    io_2 = psutil.net_io_counters()
    us, ds = io_2.bytes_sent - bytes_sent, io_2.bytes_recv - bytes_recv
    # print the total download/upload along with current speeds
    print(f"Всего отправлено: {get_size(io_2.bytes_sent - start_upload)}   "
          f"Всего загружено: {get_size(io_2.bytes_recv - start_download)}   "
          f"Скорость отправки: {get_size(us / DELAY)}/s   "
          f"Скорость загрузки: {get_size(ds / DELAY)}/s      ", end="\r")
    # update the bytes_sent and bytes_recv for next iteration
    bytes_sent, bytes_recv = io_2.bytes_sent, io_2.bytes_recv
    time.sleep(DELAY)