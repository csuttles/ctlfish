#!/usr/bin/env python3

import argparse
import shlex
import socket
import subprocess
import sys
import threading

parser = argparse.ArgumentParser(sys.argv[0])
parser.add_argument('-t', '--target', type=str, dest='target', default='0.0.0.0', help='target')
parser.add_argument('-p', '--port', type=int, dest='port', default=443, help='TCP port')
parser.add_argument('-l', '--listen', action='store_true', dest='listen', default=False, help='listen for connections')
parser.add_argument('-c', '--command', action='store_true', dest='command', default=False, help='launch a command shell')
parser.add_argument('-e', '--execute', type=str, dest='exec', default='', help='execute a command')
parser.add_argument('-u', '--upload', type=str, dest='upload', default='', help='upload this file')
parser.add_argument('-f', '--file-dest', type=str, dest='filedest', default='', help='file destination')
parser.description = "python program to do things you might normally do with netcat"
# parser.epilog = '''
# Examples:
#
# Upload local file ~/www/winbin/exploit.exe to 10.10.10.10 over port 443 and write to c:\exploit.exe on 10.10.10.10
#
#
# ./netcat.py -t 10.10.10.10 -p 443 -u ~/www/winbin/exploit.exe -f c:\exploit.exe
#
#
# Listen on port 443 and write a local file
#
# ./netcat.py -l -p 443 -f /tmp/somefile.txt
# '''
args = parser.parse_args()


def client_handler(client_socket):
    # check for upload mode
    if len(args.filedest):
        # make sure we have a path to write the file we are getting
        if not len(args.filedest):
            print(f'Could not receive upload, no -u file specified.')
            sys.exit(1)
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

                client_socket.send(f'File uploaded successfully to: {args.filedest}')
            except Exception as ex:
                client_socket.send(f'Failed to upload to: {args.filedest}\nCaught exception: {ex}')

    # check for exec mode
    if len(args.exec):
        # run the command
        output = run_command(args.exec)

        client_socket.send(bytes(output))

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
            # while True:
            #     buf = client_socket.recv(4096)
            #     if '\n' in str(buf.decode('utf-8')):
            #         cmd_buffer += buf
            #         break
            #     else:
            #         cmd_buffer += buf

            # run the command and set output as response
            print(f'running command: {cmd_buffer.decode("utf-8")}')
            response = run_command(cmd_buffer.decode('utf-8'))

            # send response to client
            print(f'sending back response: {response.decode("utf-8")}')
            client_socket.send(bytes(response) + prompt_b)


def client_sender(buffer):
    '''
    used in command mode for bidirectional communication (remote prompt)
    :param buffer: bytes
    '''
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
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

        except Exception as ex:
            print(f"client_sender caught exception:\n{ex}")
            client.close()


def server_loop():
    # args.target defaults to '0.0.0.0'
    # args.port defaults to 443
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((args.target, args.port))

        # listen with a backlog of 5 connections
        server.listen(5)

        while True:
            # define the client socket
            client_socket, addr = server.accept()

            # spin off a thread to handle connection
            client_thread = threading.Thread(target=client_handler, args=(client_socket,))
            client_thread.start()


def run_command(cmd):
    # cmd = cmd.rstrip('\n')

    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
    except ChildProcessError as ex:
        output = f"Failed to execute:\n{cmd}\nCaught exception:\n{ex}"
        raise ChildProcessError
    return output


def main():
    if not (args.listen or args.upload) and len(args.target) and args.port > 0:

        # this is a blocking select on stdin, so CTRL+D to send keyboard interrupt if you screw up (or I did) :P
        print(f'reading stdin, use CTRL+D to send EOF')
        buffer = bytes(sys.stdin.read().encode('utf-8'))
        # print(f'read this as buffer:\n{buffer.decode("utf-8")}')

        # print(f'Connecting to: {target}')
        # send data to target
        client_sender(buffer)

    if args.listen:
        server_loop()


if __name__ == '__main__':
    main()
