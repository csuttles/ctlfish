#!/usr/bin/env python3

import argparse
import sys
import socket
import threading

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-b', '--bind', type=str, dest='bind', default='0.0.0.0', help='bind address')
parser.add_argument('-p', '--port', type=int, dest='port', default=8000, help='TCP port')
args = parser.parse_args()

# create instance of socket object named "server"
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# bind to address and port
server.bind((args.bind, args.port))

# listen with a backlog of 5
server.listen(5)
print(f'[*] listening on {args.bind}:{args.port}')


# this defines our client handling thread
def handle_client(client_socket,addr):

    # print out what client sends:
    request = client_socket.recv(1024)
    print(f'[*] received from: {addr[0]}:{addr[1]}')
    print(f'{request.decode("utf-8").rstrip()}')

    # send ack
    msg = f'ack: {request.decode("utf-8")}'
    client_socket.send(bytes(msg, 'utf-8'))

    # close socket
    client_socket.close()


while True:

    # accept connection
    client, addr = server.accept()
    print(f'[*] accepted connection from: {addr[0]}:{addr[1]}')

    # call handler for this connection, spinning off a new thread to handle it
    # so the main thread can go back to listening for new connections
    client_handler = threading.Thread(target=handle_client, args=(client,addr))
    client_handler.start()
