#!/usr/bin/env python3

import argparse
import cmd
import socket
import subprocess
import sys
import threading

parser = argparse.ArgumentParser(sys.argv[0])
parser.add_argument('-t', '--target', type=str, dest='target', default='0.0.0.0', help='target')
parser.add_argument('-p', '--port', type=int, dest='port', default=443, help='TCP port')
parser.add_argument('-l', '--listen', action='store_true', dest='listen', default=False, help='listen for connections')
parser.add_argument('-e', '--execute', action='store_true', dest='command', default=False,
                    help='execute commands or emulate an interactive command shell')
parser.add_argument('-f', '--file-dest', type=str, dest='filedest', default='', help='file destination')
parser.description = """\
This is a Python program to do things you might normally do with netcat.

The idea is that this (or parts of it) are usable (or re-usable) in environments where you don't have netcat,
but you *do* have Python.
"""
args = parser.parse_args()


def client_handler(client_socket,addr):
    # check for upload mode
    if len(args.filedest):

        # make a string var as a buffer
        file_buffer = bytes()
        while True:
            data = client_socket.recv(4096)
            if not data:
                break
            else:
                file_buffer += data

            try:
                # now open a filehandle and write our buffer:
                with open(args.filedest, 'wb') as filedest:
                    filedest.write(file_buffer)

                print(f'Client: {addr[0]}:{addr[1]} uploaded successfully to: {args.filedest}')
            except Exception as ex:
                print(f'Client: {addr[0]}:{addr[1]} failed to upload to: {args.filedest}\nCaught exception: {ex}')

    # check for command mode
    if args.command:
        # Show a prompt
        # client_socket.send(bytes(r'pnetcat> '.encode('utf-8')))
        prompt_b = bytes('pnetcat> '.encode('utf-8'))
        # client_socket.send(prompt_b)

        # another loop if we want a command shell
        while True:
            # receive until linefeed
            cmd_buffer = bytes()
            while '\n' not in cmd_buffer.decode('utf-8'):
                cmd_buffer += client_socket.recv(1024)

            # run the command and set output as response
            print(f'running command: {cmd_buffer.decode("utf-8")}', end='')
            try:
                response = run_command(cmd_buffer.decode('utf-8'))

            except subprocess.CalledProcessError as error:
                c = str(error.cmd).rstrip("\n")
                r = error.returncode
                print(f'command "{c}" exited nonzero: {r}')
                # set response to bytes representation of exception so we can return it to client the same way
                response = f'command "{c}" exited nonzero: {r}\n'.encode("utf-8")
                # response = (ex.__repr__() + "\n").encode("utf-8")

            except Exception as ex:
                print(f'caught exception: {ex.__repr__()}')
                # set response to bytes representation of exception so we can return it to client the same way
                response = (ex.__repr__() + "\n").encode("utf-8")

            # send response to client
            print(f'sending response to client: {addr[0]}:{addr[1]}\n{response.decode("utf-8")}', end='')
            client_socket.send(bytes(response) + prompt_b)


def client_sender(buffer):
    '''
    used in command mode for bidirectional communication (remote prompt)
    :param buffer: bytes
    '''
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        # s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # set SO_REUSEADDR to prevent OS from blocking re-use if we end up with a connection stuck in time-wait
        try:
            client.connect((args.target, args.port))
            if len(buffer):
                # skip this to read first?
                client.send(buffer)
                # read response
                while True:
                    recv_len = 1
                    response = bytes()
                    while recv_len:
                        data = client.recv(4096)
                        recv_len = len(data)
                        response += data

                        if recv_len < 4096:
                            break
                    # print(f'read response: {response.decode("utf-8")}')

                    # read more data locally
                    buffer = bytes(input(response.decode("utf-8")).encode("utf-8"))
                    buffer += bytes('\n'.encode("utf-8"))

                    # print(f'send buffer: {buffer.decode("utf-8")}')
                    # send it over the wire
                    client.send(buffer)
        except EOFError:
            # this is expected because we will get EOF when reading the response, so just catch this and continue
            pass
        except Exception as ex:
            print(f"client_sender caught exception:\n{ex.__repr__()}")
            client.close()


def server_loop():
    # args.target defaults to '0.0.0.0'
    # args.port defaults to 443
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        # s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # set SO_REUSEADDR to prevent OS from blocking re-use if we end up with a connection stuck in time-wait
        server.bind((args.target, args.port))

        # listen with a backlog of 5 connections
        server.listen(5)

        while True:
            # define the client socket
            client_socket, addr = server.accept()

            # spin off a thread to handle connection
            client_thread = threading.Thread(target=client_handler, args=(client_socket,addr))
            client_thread.start()


def run_command(cmd):

    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
    except ChildProcessError as ex:
        output = f"Failed to execute:\n{cmd}\nCaught exception:\n{ex.__repr__()}"
        # raise ChildProcessError
        # don't actually raise this, just log so we can keep running and accept commands again from a new connection
    return output


def main():
    if not args.listen and len(args.target) and args.port > 0:
        if sys.stdin.isatty():
            # print(f'reading stdin, use CTRL+D to send EOF')
            buffer = b"\n"

        else:
            print(f'input not a TTY, assuming non-interactive, reading stdin from pipe and sending.\n')
            buffer = bytes(sys.stdin.read().encode('utf-8'))

        # buffer = bytes(sys.stdin.read().encode('utf-8'))
        client_sender(buffer)

    if args.listen:
        server_loop()


if __name__ == '__main__':
    main()
