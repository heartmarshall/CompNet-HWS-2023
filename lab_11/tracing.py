import socket
import struct
import time
import sys

sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)

sock.settimeout(1.0)

def send_icmp_request(dest_addr, ttl):
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)

    icmp_header = struct.pack('!BBHHH', 8, 0, 0, 0, 0)
    icmp_checksum = calculate_checksum(icmp_header)

    icmp_packet = struct.pack('!BBHHH', 8, 0, icmp_checksum, 0, 0)

    try:
        sock.sendto(icmp_packet, (dest_addr, 0))

        send_time = time.time()

        data, addr = sock.recvfrom(1024)
        recv_time = time.time()

        rtt = (recv_time - send_time) * 1000

        ip_addr = addr[0]

        print(f'{ip_addr} (RTT: {rtt:.2f} ms)')

    except socket.timeout:
        print('* * *')

def calculate_checksum(data):
    checksum = 0
    num_shorts = len(data) // 2

    for i in range(num_shorts):
        short = struct.unpack('!H', data[i * 2:i * 2 + 2])[0]
        checksum += short

    checksum = (checksum >> 16) + (checksum & 0xFFFF)
    checksum += (checksum >> 16)

    checksum = ~checksum & 0xFFFF

    return checksum

def traceroute(dest_addr, max_hops, num_packets):
    print(f'Traceroute to {dest_addr}:')

    for ttl in range(1, max_hops + 1):
        print(f'{ttl}.', end=' ')

        for _ in range(num_packets):
            send_icmp_request(dest_addr, ttl)

        print()

        if dest_addr in ip_addrs:
            break
destination = sys.argv[1]
max_hops = 10
num_packets = sys.argv[2]

ip_addrs = set()

traceroute(destination, max_hops, num_packets)
sock.close()
