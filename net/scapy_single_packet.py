from scapy.all import *

# packet callback
def packet_callback(packet):
  print(packet.show())

# run the sniffer
sniff(prn=packet_callback,count=1)

