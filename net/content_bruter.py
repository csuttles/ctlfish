#!/usr/bin/env python3

import argparse
import os
import psutil
import queue
import requests
import threading


parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
'''
IANAL but:

At the time of writing, this website allows testing tools and manual hacking against this intentionally vulnerable app.
It is your responsibility to use this code only for good. It is your responsibility to make sure that if you run this, 
you do not break the law.

Right now, this is included in the response from http://testphp.vulnweb.com/

Warning: This is not a real shop. This is an example PHP application, which is intentionally vulnerable to web attacks. 
It is intended to help you test Acunetix.
It also helps you understand how developer errors and bad configuration may let someone break into your website. 
You can use it to test other tools and your manual hacking skills as well. 
Tip: Look for potential SQL Injections, Cross-site Scripting (XSS), and Cross-site Request Forgery (CSRF), and more.
'''
parser.add_argument('-u', '--url', type=str, dest='url', default='http://testphp.vulnweb.com',
                    help='your target scheme and host')
parser.add_argument('-w', '--wordlist', type=str, dest='wordlist',
                    default=os.path.expanduser('~/src/SecLists/Discovery/Web-Content/big.txt'),
                    help='wordlist to use')
parser.add_argument('-f', '--firehose', dest='firehose', default=False, action='store_true',
                    help='combine all terms in wordlist for exponential firehose of brute requests')
parser.add_argument('-t', '--threads', type=int, dest='threads', default=psutil.cpu_count(),
                    help='number of worker threads to spawn, default is number of cores in system')
parser.add_argument('-m', '--method', type=str, dest='method',
                    default='get', help='http method to use for requests. valid choices are "get" and "head"')
parser.add_argument('-a', '--agent', type=str, dest='useragent',
                    default='Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:40.0) Gecko/20100101 Firefox/40.0',
                    help='User-Agent to use for requests')
parser.add_argument('-c', '--hide-codes', type=lambda s: [int(c) for c in s.split(',')], default=[404],
                    dest='hidecodes', help='list of http status codes to hide, comma-delimited')
parser.add_argument('-e', '--extensions', nargs='+', default=['.php'], dest='extensions',
                    help='list of extensions to check. must include delimiter (".php" not "php")')
parser.description = '''
This script will brute force content on a web server. 
Think wfuzz, but what would it be if you just made it up on the spot?
'''
args = parser.parse_args()


def build_terms_q(wordlist):
    terms = queue.Queue()
    with open(wordlist, 'r') as wordlistfd:
        for word in wordlistfd.readlines():
            terms.put_nowait(word.rstrip())
    return terms


def dir_brute(terms_q, extensions=None):
    sess = requests.Session()
    while not terms_q.empty():
        attempt = terms_q.get()
        attempt_list = []

        # build out a map of attempts / variations for this term
        if args.firehose:
            # add as both a "file" and a "dir" to maximize wordlists
            attempt_list.append(f'/{attempt}/')
            attempt_list.append(f'/{attempt}')

        else:
            # check for file ext to determine if we want to do dir things of file things
            if '.' not in attempt:
                # add it with a trailing slash, voila: it's a dir
                attempt_list.append(f'/{attempt}/')
            else:
                # add it with no slash, voila: it's a file
                attempt_list.append(f'/{attempt}')

        # do we want to brute force specific extensions?
        if extensions:
            for ext in extensions:
                # important to note that ext should be formatted with the delimiter - [ '.cgi', '.pl', '.php', ',phps' ]
                attempt_list.append(f'{attempt}{ext}')

        # do the requests
        for brute in attempt_list:
            # book example has us urlquote here, but requests does that for free
            url = f'{args.url}{brute}'

            try:
                headers = {'User-Agent': args.useragent}
                if args.method.lower() == 'head':
                    resp = sess.head(url=url, headers=headers)
                else:
                    # this is the default
                    resp = sess.get(url=url, headers=headers)

                if resp.status_code not in args.hidecodes:
                    print(f'{resp.status_code} => {url}')
            except UnicodeError:
                # ignore unicode errors in wordlists
                pass
            except requests.exceptions.ConnectionError:
                pass
            except requests.exceptions.RequestException as ex:
                print(f'caught exception {ex.__class__.__name__} - {ex}')
                pass


def dump_q(terms_q):
    while True:
        if terms_q.empty():
            break
        word = terms_q.get()
        print(f'{threading.current_thread().getName()}:{word}')


def main():
    print(args)

    words = build_terms_q(args.wordlist)

    threads = []
    for tid in range(args.threads):
        print(f'spawning thread: {tid}')
        t = threading.Thread(target=dir_brute, args=(words, args.extensions), name=f'worker-{tid}')
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
    print('all done.')


if __name__ == '__main__':
    main()
