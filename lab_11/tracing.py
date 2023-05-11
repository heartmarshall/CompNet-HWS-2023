import socket
import struct
import time

# Create a raw socket using ICMP protocol
sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)

# Set the timeout for the socket
sock.settimeout(1.0)

def send_icmp_request(dest_addr, ttl):
    # Set the IP TTL field
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)

    # Create an ICMP Echo Request packet
    icmp_header = struct.pack('!BBHHH', 8, 0, 0, 0, 0)
    icmp_checksum = calculate_checksum(icmp_header)

    # Insert the checksum into the packet
    icmp_packet = struct.pack('!BBHHH', 8, 0, icmp_checksum, 0, 0)

    try:
        # Send the ICMP packet to the destination
        sock.sendto(icmp_packet, (dest_addr, 0))

        # Record the time when the packet was sent
        send_time = time.time()

        # Receive the response packet
        data, addr = sock.recvfrom(1024)
        recv_time = time.time()

        # Calculate the RTT in milliseconds
        rtt = (recv_time - send_time) * 1000

        # Extract the IP address from the response packet
        ip_addr = addr[0]

        print(f'{ip_addr} (RTT: {rtt:.2f} ms)')

    except socket.timeout:
        # Handle timeout if no response is received
        print('* * *')

def calculate_checksum(data):
    checksum = 0
    num_shorts = len(data) // 2

    # Iterate through the data in 16-bit chunks
    for i in range(num_shorts):
        short = struct.unpack('!H', data[i * 2:i * 2 + 2])[0]
        checksum += short

    # Add the carry bits to the checksum
    checksum = (checksum >> 16) + (checksum & 0xFFFF)
    checksum += (checksum >> 16)

    # One's complement the checksum
    checksum = ~checksum & 0xFFFF

    return checksum

def traceroute(dest_addr, max_hops, num_packets):
    print(f'Traceroute to {dest_addr}:')

    for ttl in range(1, max_hops + 1):
        print(f'{ttl}.', end=' ')

        for _ in range(num_packets):
            send_icmp_request(dest_addr, ttl)

        print()

        # Check if the destination is reached
        if dest_addr in ip_addrs:
            break

# Set the destination address and maximum number of hops
destination = 'ya.ru'
max_hops = 10
num_packets = 3

# Initialize a set to store unique IP addresses
ip_addrs = set()

# Perform the traceroute
traceroute(destination, max_hops, num_packets)

# Close the socket
sock.close()
