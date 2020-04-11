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

## mail_sniffer.py

This is a test run with a 2 line ish sniffer with python3 on kali 2020

```
kali@kali:[~/src/ctlfish/net]:(master *+)
[Exit: 0] 17:51: sudo python3 mail_sniffer.py
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
