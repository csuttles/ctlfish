#!/usr/bin/env python3

import argparse
import asyncio
import readline
import sys

parser = argparse.ArgumentParser()
parser.add_argument('-H', '--host', type=str, dest='host', default=None, help='IP addr of host')
parser.add_argument('-p', '--port', type=int, dest='port', default=80, help='TCP port')
args = parser.parse_args()


async def main():
    reader, writer = await asyncio.open_connection(args.host, args.port)
    print(f'connected to: {args.host}:{args.port}')
    try:
        while True:
            line = input('> ')
            line += '\n'
            writer.write(bytes(line, "utf-8"))
            await writer.drain()

            data = await reader.read(4096)
            print(bytes(data).decode("utf-8"))

    except KeyboardInterrupt:
        print(f'Caught KB interrupt, exiting.')
        sys.exit(1)
    finally:
        writer.close()
        await writer.wait_closed()


if __name__ == '__main__':
    asyncio.run(main())
