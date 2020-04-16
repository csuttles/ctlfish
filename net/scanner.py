#!/usr/bin/env python3

import argparse
import os
import readline
import socket
import struct
import sys
import threading
import time

from ctypes import *
from netaddr import IPNetwork, IPAddress

readline.get_history_length()
# throw this away because we import readline for prompt stuff
parser = argparse.ArgumentParser(sys.argv[0])
parser.add_argument('-l', '--listen', type=str, dest='listen', default='0.0.0.0',
                    help='address to bind and sniff packets')
parser.add_argument('-s', '--subnet', type=str, dest='subnet', default='192.168.1.0/24',
                    help='subnet to scan')
parser.add_argument('-m', '--message', type=str, dest='message', default='ctlfish',
                    help='message to embed in UDP scan to help identify responses')

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

    def __init__(self, socket_buffer):

        # map protocol constants to names
        self.protocol_map = {1: "ICMP", 6: "TCP", 17: "UDP"}

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


class ICMP(Structure):

    _fields_ = [
        ('type',            c_ubyte),
        ('code',            c_ubyte),
        ('checksum',        c_ushort),
        ('unused',          c_ushort),
        ('next_hop_mtu',    c_ushort)
    ]

    def __new__(cls, socket_buffer=None):
        return cls.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer):
        pass


def udp_sender(subnet, message):
    time.sleep(5)
    sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    for ip in IPNetwork(subnet):
        try:
            # we have to convert ip to str because it is a IPAddress object and socket will silently fail because UDP.
            sz = sender.sendto(bytes(message, 'utf-8'), (str(ip), 31337))
            print(f'Sent {message} ({sz} bytes) to {ip}')
        except:
            pass
    return None


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

    # # start sending udp packets so we can sniff responses
    t = threading.Thread(target=udp_sender, args=(args.subnet, args.message), daemon=True)
    t.start()

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

            # snag ICMP for further dissection
            if ip_header.protocol == 'ICMP':

                # calculate start of ICMP and grab buffer
                offset = ip_header.ihl * 4
                icmp_buf = raw_buffer[offset:offset + sizeof(ICMP)]

                # init our struct
                icmp_header = ICMP(icmp_buf)

                print(f'ICMP -> Type: {icmp_header.type} Code: {icmp_header.code}')

                # check for type 3 && code 3 which means destination port unreachable
                # if we get a ICMP saying unreachable, this means a host is up to send that ICMP reply
                if icmp_header.code == 3 and icmp_header.type == 3:

                    # make sure host is in scope (in target subnet)
                    if IPAddress(ip_header.src_address) in IPNetwork(args.subnet):

                        # make sure we got the magic message (indicating it is a response to our UDP spray)
                        if raw_buffer[len(raw_buffer) - len(args.message):] == bytes(args.message, 'utf-8'):
                            print(f'Host up: {ip_header.src_address}')


    except KeyboardInterrupt:
        print(f'Caught KB interrupt, exiting.')
        sys.exit(1)

    # if windows explicitly unset promiscuous mode to clean up
    if os.name == 'nt':
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)


if __name__ == '__main__':
    main()
