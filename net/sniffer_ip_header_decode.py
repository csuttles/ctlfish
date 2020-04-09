#!/usr/bin/env python3

import argparse
import os
import readline
import socket
import struct
import subprocess
import sys
import threading

from ctypes import *

readline.get_history_length()
# throw this away because we import readline for prompt stuff
parser = argparse.ArgumentParser(sys.argv[0])
parser.add_argument('-l', '--listen', type=str, dest='listen', default='0.0.0.0',
                    help='address to bind and sniff packets')
parser.description = """\
This is a Python program to scan a network for live hosts by spraying UDP traffic and inspecting responses.
"""
args = parser.parse_args()


class IP(Structure):
    # https://stackoverflow.com/questions/29306747/python-sniffing-from-black-hat-python-book/29307402
    # correct data types so that endian-ness is correct/native regardless of platform
    _fields_ = [
        ('ihl',             c_ubyte, 4),
        ('version',         c_ubyte, 4),
        ('tos',             c_ubyte, 8),
        ('len',             c_ushort, 16),
        ('id',              c_ushort, 16),
        ('flags',           c_ubyte, 3),
        ('offset',          c_ushort, 13),
        ('ttl',             c_ubyte, 8),
        ('protocol_num',    c_ubyte, 8),
        ('sum',             c_ushort, 16),
        # ('src',             c_ulong, 32),
        # ('dst',             c_ulong, 32)
        ('src',             c_uint32),
        ('dst',             c_uint32)
    ]

    def __new__(cls, socket_buffer=None):
        return cls.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer=None):

        # map protocol constants to names
        self.protocol_map = {1: "ICMP", 6: "TCP", 17: "UDP"}

        # when the examples don't work so you print everything and fix header field lengths 1x1 with RFC magic
        # _and_ you can use your own blog as reference https://blog.csuttles.io/a-brief-comparison-of-ipv4-and-ipv6/
        # print(f'ihl: {self.ihl}', len(str(self.ihl)))
        # print(f'version: {self.version}', len(str(self.version)))
        # print(f'tos: {self.tos}', len(str(self.tos)))
        # print(f'len: {self.len}', len(str(self.len)))
        # print(f'id: {self.id}', len(str(self.id)))
        # print(f'offset: {self.offset}', len(str(self.offset)))
        # print(f'ttl: {self.ttl}', len(str(self.ttl)))
        # print(f'protocol_num: {self.protocol_num}', len(str(self.protocol_num)))
        # print(f'sum: {self.sum}', len(str(self.sum)))
        # print(f'src: {self.src}', len(str(self.src)))
        # print(f'dst: {self.dst}', len(str(self.dst)))

        # readable ip addresses
        # https://stackoverflow.com/questions/29306747/python-sniffing-from-black-hat-python-book/29307402
        # correct data types so that endian-ness is correct/native regardless of platform
        # self.src_address = socket.inet_ntoa(struct.pack("<L", self.src))
        # self.dst_address = socket.inet_ntoa(struct.pack("<L", self.dst))
        self.src_address = socket.inet_ntoa(struct.pack("@I", self.src))
        self.dst_address = socket.inet_ntoa(struct.pack("@I", self.dst))

        # try to map human readable proto
        try:
            self.protocol = self.protocol_map[self.protocol_num]
        except:
            self.protocol = str(self.protocol_num)


def main():
    # make this work on windows too
    if os.name == 'nt':
        socket_protocol = socket.IPPROTO_IP
    else:
        socket_protocol = socket.IPPROTO_ICMP

    # set up raw socket and bind
    sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)
    sniffer.bind((args.listen, 0))
    # we want to include headers
    sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    # if windows explicitly set promiscuous mode
    if os.name == 'nt':
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

    # start sniffing and decoding
    try:
        while True:
            # read a single packet - I caught this size error on first read, yay (author uses 65565)
            raw_buffer = sniffer.recvfrom(65535)[0]
            if not raw_buffer:
                break

            # create ip header from first 32 bytes
            ip_header = IP(socket_buffer=raw_buffer[0:20])

            # print the decoded protocol and addrs
            print(f'Protocol: {ip_header.protocol} {ip_header.src_address} -> {ip_header.dst_address}')

    except KeyboardInterrupt:
        print(f'Caught KB interrupt, exiting.')
        sys.exit(1)

    # if windows explicitly unset promiscuous mode to clean up
    if os.name == 'nt':
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)


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


if __name__ == '__main__':
    main()
