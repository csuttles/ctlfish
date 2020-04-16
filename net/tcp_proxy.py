#!/usr/bin/env python3

import argparse
import socket
import subprocess
import sys
import threading

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-r', '--rhost', type=str, dest='rhost', default='127.0.0.1', help='remote host address')
parser.add_argument('-P', '--rport', type=int, dest='rport', default=9999, help='remote TCP port')
parser.add_argument('-l', '--lhost', type=str, dest='lhost', default='127.0.0.1', help='local host address')
parser.add_argument('-p', '--lport', type=int, dest='lport', default=9050, help='local TCP port')
parser.add_argument('-f', '--receive-first', action='store_true', dest='recvfirst',
                    default=False, help='flag to receive data before sending once we connect to rhost:rport')
parser.description = """\
This is a Python program to run a TCP proxy. It listens on one address/port (local) and forwards to another 
address/port (can be local or remote).
"""
args = parser.parse_args()


def proxy_handler(client_socket, addr, rhost, rport, recvfirst):
    """
    handler for when we get a client connection to this proxy

    :param client_socket: the client socket we get from socket.accept()
    :param addr: the client addr we get from socket.accept()
    :param rhost: the remote host
    :param rport: the remote port
    :param recvfirst: receive data before we send
    :return:
    """
    # open remote socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as remote_socket:
        remote_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        remote_socket.connect((rhost, rport))

        # will we recvfirst?
        if recvfirst:
            # if so read remote buffer and print it
            remote_buffer = receive_from(remote_socket)
            print(f'received: {len(remote_buffer)} bytes from: {rhost}:{rport}')
            hexdump(remote_buffer)

            # send to response_handler (hook where we can change packets)
            remote_buffer = response_handler(remote_buffer)

            # if we have data to send, then send it
            if len(remote_buffer):
                client_socket.send(remote_buffer)
                print(f'sent: {len(remote_buffer)} bytes to: {addr[0]}:{addr[1]}')

        # now we loop and read from local, send to remote
        while True:
            local_buffer = receive_from(client_socket)

            if len(local_buffer):
                print(f'received: {len(local_buffer)} bytes from: {addr[0]}:{addr[1]}')
                hexdump(local_buffer)

                # send to request handler (hook to change packets)
                local_buffer = request_handler(local_buffer)

                # send to remote
                remote_socket.send(local_buffer)
                print(f'sent: {len(local_buffer)} bytes to: {rhost}:{rport}')

                # receive the response
                remote_buffer = receive_from(remote_socket)

                if len(remote_buffer):
                    print(f'received: {len(remote_buffer)} bytes from: {rhost}:{rport}')
                    hexdump(remote_buffer)

                    # send to response handler (hook to change packets)
                    remote_buffer = response_handler(remote_buffer)

                    # send response to local socket
                    client_socket.send(remote_buffer)
                    print(f'sent: {len(remote_buffer)} bytes to: {addr[0]}:{addr[1]}')

                # if no more data on either side, close connections
                if not len(local_buffer) or not len(remote_buffer):
                    print(f'no more data, closing connection with {rhost}:{rport}')
                    # client_socket.close() # this didn't seem like it was working
                    # also a proxy should continue to listen even if clients come and go
                    remote_socket.close()
                    break


def hexdump(src, length=16, sep='.'):
    """
    https://gist.github.com/1mm0rt41PC/c340564823f283fe530b
    """
    result = []

    for i in range(0, len(src), length):
        subSrc = src[i:i + length]
        hexa = ''
        for h in range(0, len(subSrc)):
            if h == length / 2:
                hexa += ' '
            h = subSrc[h]
            if not isinstance(h, int):
                h = ord(h)
            h = hex(h).replace('0x', '')
            if len(h) == 1:
                h = '0' + h
            hexa += h + ' '
        hexa = hexa.strip(' ')
        text = ''
        for c in subSrc:
            if not isinstance(c, int):
                c = ord(c)
            if 0x20 <= c < 0x7F:
                text += chr(c)
            else:
                text += sep
        result.append(('%08X:  %-' + str(length * (2 + 1) + 1) + 's  |%s|') % (i, hexa, text))

    print('\n'.join(result))


def receive_from(connection):
    """

    :param connection: established socket connection
    :return: buffer received from socket
    """
    buffer = bytes()

    # This timeout gets repeated between each read/send so stay low or things will become very slow.
    # Removing this makes things break. ;)
    connection.settimeout(1)

    try:
        # keep reading until no data or we timeout
        while True:
            data = connection.recv(4096)
            if not data:
                break
            buffer += data

    except Exception:
        pass

    return buffer


def request_handler(buf):
    # this is where we modify packets
    return buf


def response_handler(buf):
    # this is where we modify packets
    return buf


def server_loop(lhost, lport, rhost, rport, recvfirst):
    """
    Bind and listen for connections, spawn a handler for each connection.

    args.lhost defaults to '127.0.0.1'
    args.lport defaults to 9050
    """

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # set SO_REUSEADDR to prevent OS from blocking re-use if we end up with a connection stuck in time-wait
        server.bind((lhost, lport))

        # listen with a backlog of 5 connections
        server.listen(5)

        while True:
            # define the client socket
            client_socket, addr = server.accept()
            print(f'accepted connection from: {addr[0]}:{addr[1]}')

            # spin off a thread to handle connection
            proxy_thread = threading.Thread(target=proxy_handler, args=(client_socket, addr, rhost, rport, recvfirst))
            proxy_thread.start()


def main():
    # do stuff
    if not (args.lhost and args.lport and args.rhost and args.rport):
        raise ValueError("Not enough args. Please see usage.")

    # listen for connections
    server_loop(args.lhost, args.lport, args.rhost, args.rport, args.recvfirst)


if __name__ == '__main__':
    main()
