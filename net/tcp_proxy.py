#!/usr/bin/env python3

import argparse
import socket
import subprocess
import sys
import threading

parser = argparse.ArgumentParser(sys.argv[0])
parser.add_argument('-r', '--rhost', type=str, dest='rhost', default='127.0.0.1', help='remote host address')
parser.add_argument('-P', '--rport', type=int, dest='rport', default=9999, help='remote TCP port')
parser.add_argument('-l', '--lhost', type=str, dest='lhost', default='127.0.0.1', help='local host address')
parser.add_argument('-p', '--lport',  type=int, dest='lport', default=9050, help='local TCP port')
parser.description = """\
This is a Python program to run a TCP proxy. It listens on one address/port (local) and forwards to another 
address/port (can be local or remote).
"""
args = parser.parse_args()


def client_handler(client_socket, addr):
    # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as outpipe:
    #     outpipe.connect((args.rhost,args.port))

def server_loop():
    """
    Bind and listen for connections, spawn a handler for each connection.

    args.lhost defaults to '127.0.0.1'
    args.lport defaults to 9050
    """

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # set SO_REUSEADDR to prevent OS from blocking re-use if we end up with a connection stuck in time-wait
        server.bind((args.lhost, args.lport))

        # listen with a backlog of 5 connections
        server.listen(5)

        while True:
            # define the client socket
            client_socket, addr = server.accept()

            # spin off a thread to handle connection
            client_thread = threading.Thread(target=client_handler, args=(client_socket, addr))
            client_thread.start()


def main():
    # do stuff
    if not (args.lhost and args.lport and args.rhost and args.rport):
        raise ValueError("Not enough args. Please see usage.")



    # listen for connections
    server_loop()


if __name__ == '__main__':
    main()