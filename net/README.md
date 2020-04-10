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
