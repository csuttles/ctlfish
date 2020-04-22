#!/usr/bin/env python3

import argparse
import os
import psutil
import queue
import requests
import threading

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-t', '--target', type=str, dest='target', default='http://localhost:8000',
                    help='your target scheme and host')
parser.add_argument('-d', '--directory', type=str, dest='dir', default='/tmp',
                    help='local directory to use')
parser.add_argument('-w', '--workers', type=int, dest='threads', default=psutil.cpu_count(),
                    help='number of worker threads to spawn, default is number of cores in system')
parser.add_argument('-f', '--filter', type=str, nargs='+', dest='filters',
                    default=['.png', '.gif', '.jpg', '.jpeg', '.css'], help='file suffixes to filter out')
parser.description = '''
This script will brute force a remote machine over http to discover directories by walking your local 
directory to build a list of paths to check, then spawn a pool of threads to check them on the target.

example: you suspect the target is running Joomla - you download and extract Joomla, then run this script 
 from inside the local Joomla dir, and every file that is included by default will be tried on the target. 
 You can take that a step further and use mkdir and touch to create local files and dirs you suspect may exist.
 maybe use find and touch to create munged names before you run this tool to check if the paths exist on the target. 
'''
args = parser.parse_args()


print(f'changing dir to {args.dir}')
os.chdir(args.dir)

rel_urls = queue.Queue()

for rootdir, dirs, nondirs in os.walk('.'):
    for files in nondirs:
        rpath = f'{rootdir}/{files}'
        if rpath.startswith('.'):
            rpath = rpath[1:]
        # skip all the extensions in our filter
        if os.path.splitext(files)[1] not in args.filters:
            # /includes/leading/slash
            rel_urls.put_nowait(rpath)


def test_remote():
    sess = requests.session()
    while not rel_urls.empty():
        rel_url = rel_urls.get()
        url = f'{args.target}{rel_url}'
        try:
            resp = sess.get(url)
            print(f'{resp.status_code} => {rel_url}')
        except Exception as ex:
            print(f'caught exception: {ex.__class__.__name__} - {ex}')
            # mostly just catches connection errors to suppress them
            pass


for tid in range(args.threads):
    print(f'spawning thread: {tid}')
    t = threading.Thread(target=test_remote, name=f'worker-{tid}')
    t.start()
