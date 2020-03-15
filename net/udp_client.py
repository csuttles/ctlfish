#!/usr/bin/env python3

import argparse
import sys
import socket

parser = argparse.ArgumentParser()
parser.add_argument('-H', '--host', type=str, metavar='host', default=None, help='IP addr of host')
parser.add_argument('-p', '--port', type=int, metavar='port', default=80, help='UDP port')
args = parser.parse_args()

print(f"Connecting to: {args.host}:{args.port}")
# bridge udp to tcp with socat because http doesn't listen on UDP
# bridge is ONE WAY
# socat -u udp-recvfrom:3333,fork tcp:localhost:7777

# create a socket object
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# UDP is YOLO, so we start off by sending some data
send_msg = b'GET / HTTP/1.0\r\n\r\n'
print(f'sending:\n{send_msg.decode("utf-8")}')
client.sendto(send_msg, (args.host, args.port))

# recv some the response
response, addr = client.recvfrom(4096)

# when we exit the context manager we implicitly clean up the socket
print(response.decode('utf-8'))

# exit 0 to indicate success
sys.exit(0)
