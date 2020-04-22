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

## IANAL

I am not a lawyer

It is your responsibility to use this code only for good. It is your responsibility to make sure that if you run this,
you do not break the law.

## Feature requests and bugfixes

Send me a PR, and I'll probably accept it. :D

## What's with the name?

It's related to [my activities on hackthebox.eu](https://www.hackthebox.eu/profile/235518) and other ethical hacking endeavors.

# Examples

In the examples that follow, the hostname `kali` is a kali linux machine, probably running at least the 2020.1 release.
The hostname `jabroni` is a mac running recent (2020) Apple stuff and brew packages. Hopefuly this can help provide some context
on where things should work, although it probably will take a bit of elbow grease and/or configuration on the part of the reader.

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
[Exit: 0] 10:07: sudo ./arper.py -g 192.168.1.1 -t 192.168.1.132 -i eth0 -f arper.pcap
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
writing original image to: ./pictures/bigface.pcap-pic_carver_2.jpeg
writing original image to: ./pictures/bigface.pcap-pic_carver_3.jpeg
...
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

## content_bruter.py

This is a brute force tool for discovering content over http

### run the tool with mostly default options and a popular seclist

My SecLists dir is the venerated [SecLists by Daniel Miessler](https://github.com/danielmiessler/SecLists), but of course you can use any wordlist you like with the tool.

```
kali@jabroni:[~/src/ctlfish/net]:(master *)
[Exit: 1] 10:05: ./content_bruter.py -u 'http://testphp.vulnweb.com' -w ~/src/SecLists/Discovery/Web-Content/common.txt -m 'head' -f -c 404,429  -a ctlfish -e .php .cgi
url: http://testphp.vulnweb.com
wordlist: /Users/csuttles/src/SecLists/Discovery/Web-Content/common.txt
firehose: True
threads: 16
method: head
useragent: ctlfish
hidecodes: [404, 429]
extensions: ['.php', '.cgi']
spawning thread: 0
spawning thread: 1
spawning thread: 2
spawning thread: 3
spawning thread: 4
spawning thread: 5
spawning thread: 6
spawning thread: 7
spawning thread: 8
spawning thread: 9
spawning thread: 10
spawning thread: 11
spawning thread: 12
spawning thread: 13
spawning thread: 14
spawning thread: 15
200 => http://testphp.vulnweb.com/CVS/Repository
200 => http://testphp.vulnweb.com/CVS/Entries
200 => http://testphp.vulnweb.com/CVS/Root
301 => http://testphp.vulnweb.com/CVS
200 => http://testphp.vulnweb.com/CVS/
301 => http://testphp.vulnweb.com/admin
200 => http://testphp.vulnweb.com/admin/
403 => http://testphp.vulnweb.com/cgi-bin
403 => http://testphp.vulnweb.com/cgi-bin/
403 => http://testphp.vulnweb.com/cgi-bin//
403 => http://testphp.vulnweb.com/cgi-bin/
200 => http://testphp.vulnweb.com/crossdomain.xml
200 => http://testphp.vulnweb.com/favicon.ico
301 => http://testphp.vulnweb.com/images
200 => http://testphp.vulnweb.com/images/
200 => http://testphp.vulnweb.com/index.php
301 => http://testphp.vulnweb.com/pictures
200 => http://testphp.vulnweb.com/pictures/
301 => http://testphp.vulnweb.com/secured
200 => http://testphp.vulnweb.com/secured/
all done.
```


### watch traffic via tshark

I grabbed the ip address for testphp.vulnweb.com via `dig +short testphp.vulnweb.com`, which is the host I am filtering here (176.28.50.165).

One reason to do this with tshark is that you can leverage the displayfilters. I also like to do `-O http` for details on _just_ http.

```
kali@jabroni:[~/src/ctlfish/net]:(master)
[Exit: 0] 07:24: sudo tshark -i en0 -nn -Y 'ip.host == "176.28.50.165" and http'
Capturing on 'Wi-Fi: en0'
   67   0.146576 192.168.86.102 → 176.28.50.165 HTTP 214 HEAD /analog.html/ HTTP/1.1
   68   0.146662 192.168.86.102 → 176.28.50.165 HTTP 210 HEAD /amember/ HTTP/1.1
   70   0.149519 192.168.86.102 → 176.28.50.165 HTTP 210 HEAD /analyse/ HTTP/1.1
   71   0.149667 192.168.86.102 → 176.28.50.165 HTTP 209 HEAD /analog/ HTTP/1.1
   75   0.153132 192.168.86.102 → 176.28.50.165 HTTP 212 HEAD /analytics/ HTTP/1.1
   76   0.153193 192.168.86.102 → 176.28.50.165 HTTP 211 HEAD /analysis/ HTTP/1.1
   90   0.169928 192.168.86.102 → 176.28.50.165 HTTP 205 HEAD /and HTTP/1.1
  108   0.192590 192.168.86.102 → 176.28.50.165 HTTP 209 HEAD /android HTTP/1.1
  124   0.224251 192.168.86.102 → 176.28.50.165 HTTP 210 HEAD /announce HTTP/1.1
  125   0.225749 192.168.86.102 → 176.28.50.165 HTTP 214 HEAD /announcement HTTP/1.1
```
