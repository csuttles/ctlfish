import re
from scapy.all import *

# packet callback
from scapy.layers.inet import TCP, IP


def packet_callback(packet):
    if packet.haslayer(TCP) and packet[TCP].payload:

        # do we get a payload?
        # print(packet.show())
        mail_packet = packet[TCP].payload

        # if "user" in mail_packet.lower() or "pass" in mail_packet.lower():
        pattern = re.compile('(.*(?:user|pass|login|auth).*)', re.IGNORECASE)
        m = re.search(pattern, str(mail_packet))
        if m:
            print('match: ', m.group(1))
            print('Server: %s' % packet[IP].dst)
            print(mail_packet)


# run the sniffer
# sniff(prn=packet_callback,filter='tcp port 110 or tcp port 25 or tcp port 143', store=0)
# sniff on loopback for testing locally
sniff(prn=packet_callback, filter='tcp port 110 or tcp port 25 or tcp port 143', iface='lo', store=0)
