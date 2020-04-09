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

### define ip struct
#
#   This is just a map for later to build a class with these types in the right syntax.
#
###
# struct ip {
#     u_char  ip_hl:4
#     u_char  ip_v:4
#     u_char  ip_tos
#     u_short ip_len
#     u_short ip_id
#     u_short ip_off
#     u_char  ip_ttl
#     u_char  ip_p
#     u_short ip_sum
#     u_long  ip_src
#     u_long  ip_dst
# }


def main():
    # make this work on windows too
    if os.name == 'nt':
        socket_protocol = socket.IPPROTO_IP
    else:
        socket_protocol = socket.IPPROTO_ICMP

    # set up raw socket and bind
    sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)
    sniffer.bind((args.listen,0))
    # we want to include headers
    sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    # if windows explicitly set promiscuous mode
    if os.name == 'nt':
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

    # read a single packet
    data = sniffer.recv(65536)
    print(data)
    hexdump(data)

    # if windows explicitly set promiscuous mode
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
