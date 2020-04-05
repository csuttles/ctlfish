#!/usr/bin/env python3

import argparse
import asyncio
import sys

parser = argparse.ArgumentParser(sys.argv[0])
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


async def proxy_handler(local_reader: asyncio.StreamReader, local_writer: asyncio.StreamWriter):
    """
    invoked as callback when we receive a connection.

    The client_connected_cb callback is called whenever a new client connection is established.
    It receives a (reader, writer) pair as two arguments, instances of the StreamReader and StreamWriter classes.
    :param local_reader:
    :param local_writer:
    :return:
    """
    # open connection to forward packets
    remote_reader, remote_writer = await asyncio.open_connection(
        args.rhost, args.rport)
    # set local_addr, remote_addr so we can print nice messages
    local_addr = local_writer.get_extra_info('peername')
    remote_addr = remote_writer.get_extra_info('peername')

    # will we recvfirst?
    if args.recvfirst:
        # will the server send us a banner or prompt on connection?
        # if so read remote buffer and print it
        remote_data = await remote_reader.read(4096)
        print(f"Received from {remote_addr}")
        hexdump(remote_data)

        # send to local_mangle (hook where we can change packets)
        remote_data = remote_mangle(remote_data)

        # if we have data to send, then send it
        if len(remote_data):
            # send to remote_mangle (hook where we can change packets)
            local_data = local_mangle(remote_data)

            if len(local_data):
                local_writer.write(local_data)
                await local_writer.drain()
                print(f"Sent to {local_addr}")

    # now we loop and read from local, send to remote
    while True:
        # read request / print
        # todo: why does everything break without this sleep?
        await asyncio.sleep(0.1)
        local_data = await local_reader.read(4096)
        print(f"Received from {local_addr}")
        hexdump(local_data)

        # send to local_mangle (hook where we can change packets)
        local_data = local_mangle(local_data)

        # send to remote
        remote_writer.write(local_data)
        await remote_writer.drain()
        print(f"Sent to {remote_addr}")

        # receive the response
        # todo: why does everything break without this sleep?
        await asyncio.sleep(0.1)
        remote_data = await remote_reader.read(4096)

        # if len(remote_data):
        if not len(remote_data):
            break

        print(f"Received from {remote_addr}")
        hexdump(remote_data)

        # send to response handler (hook to change packets)
        remote_data = remote_mangle(remote_data)

        # send response to local socket
        local_writer.write(remote_data)
        await local_writer.drain()
        print(f"Sent to {local_addr}")

    remote_writer.close()
    await remote_writer.wait_closed()


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


def local_mangle(buf):
    return buf


def remote_mangle(buf):
    return buf


async def main():
    # do stuff
    if not (args.lhost and args.lport and args.rhost and args.rport):
        raise ValueError("Not enough args. Please see usage.")

    # listen for connections
    server = await asyncio.start_server(
        client_connected_cb=proxy_handler,
        host=args.lhost, port=args.lport)

    local_addr = server.sockets[0].getsockname()
    print(f'serving on {local_addr}')

    async with server:
        await server.serve_forever()


if __name__ == '__main__':
    asyncio.run(main(), debug=True)
