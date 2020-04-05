#!/usr/bin/env python3

from binascii import hexlify
import os
import paramiko
import socket
import sys
import threading

host_key = paramiko.RSAKey(filename='/etc/ssh/ssh_host_rsa_key')
priv_key = os.path.expanduser('~/.ssh/id_rsa')


class Server(paramiko.ServerInterface):

    def __init__(self):
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_publickey(self, username, key):
        if (username):
        # silly hack for PoC so we don't even check username content.
        # if (username == 'derp'):
            # dump fingerprint of client key
            print("Auth attempt with key: " + (hexlify(key.get_fingerprint())).decode("utf-8"))
            # set and dump fingerprint of key we load to compare
            good_pub_key = paramiko.RSAKey.from_private_key_file(priv_key)
            print("Try to compare with key: " + (hexlify(good_pub_key.get_fingerprint())).decode("utf-8"))
            # success if they are the same key
            if good_pub_key == key:
                return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED


if len(sys.argv) < 3:
    print(f'usage: {sys.argv[0]} <server> <port>')
    sys.exit(1)

server = sys.argv[1]
port = int(sys.argv[2])

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((server, port))
    sock.listen(100)
    print(f'listening for connection on {server}:{port}')
    client, addr = sock.accept()
except Exception as ex:
    print(f'listening failed on {server}:{port}\nGot exception:{ex}')
    sys.exit(1)
print(f'Got a connection!')

try:
    # noinspection PyTypeChecker
    this_session = paramiko.Transport(client)
    this_session.add_server_key(host_key)
    server = Server()
    try:
        this_session.start_server(server=server)
    except paramiko.SSHException as ex:
        print(f'SSH negotiation failed with exception: {ex}')
    chan = this_session.accept(timeout=30)
    print(f'Authenticated client: {addr[0]}:{addr[1]}')
    print(chan.recv(1024).decode("utf-8"))
    chan.send('welcome to ctlfish ssh server, please enter commands in the other side of this session')
    while True:
        try:
            cmd = input('> ').strip('\n')
            if cmd != 'exit':
                chan.send(cmd)
                data = bytes()
                # fix example splitting large reads in a real funky/unusable way
                # print(chan.recv(1024).decode("utf-8") + '\n')
                while True:
                    buf = chan.recv(1024)
                    data += buf
                    if len(buf) < 1024:
                        break
                print(data.decode("utf-8") + '\n')
            else:
                chan.send('exit')
                print(f'exiting')
                this_session.close()
                raise Exception('exit')
        except KeyboardInterrupt:
            this_session.close()
            sys.exit(1)

except KeyboardInterrupt:
    print(f'caught exception: {ex.__class__()} {str(ex)}')
    try:
        this_session.close()
    except Exception:
        pass
    sys.exit(1)
