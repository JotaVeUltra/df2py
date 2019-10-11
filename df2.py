#!/usr/bin/env python
"""
Usage:
    df2 <path>... [--quiet --output=OUTPUT --like=LIKE --size]

Options:
    -q --quiet
    -o --output=OUTPUT
    -h --help
    -l --like=LIKE
    -s --size
"""

from collections import defaultdict
from docopt import docopt
from functools import lru_cache
from hashlib import md5
from os import remove, walk
from os.path import join
from pprint import pformat


BLOCKSIZE = 65536

@lru_cache(maxsize=None)
def md5_hash(file_path):
    """
    Returns the md5 hexadecimal hash of a given file
    """
    md5_hasher = md5()
    with open(file_path, 'rb') as f:
        while True:
            buf = f.read(BLOCKSIZE)
            if not buf:
                break
            md5_hasher.update(buf)
    return md5_hasher.hexdigest()

def df(paths, q, like):
    """
    Returs a dict of set to every file under given paths
    """
    hash_dict = defaultdict(set)
    if like:
        like_hash = md5_hash(like)
        hash_dict[like_hash].add(like)
    for path in paths:
        for directory in walk(path):
            directory_path = directory[0]
            if not q:
                print(directory_path)
            files = directory[2]
            for f in files:
                h = md5_hash(join(directory_path,f))
                hash_dict[h].add(join(directory_path,f))
    if like:
        return {like_hash: hash_dict[like_hash]}
    return hash_dict

if __name__ == '__main__':
    """
    Take any number of paths received as arg and write the path of every file that has a duplicate
    """
    arguments = docopt(__doc__)
    file_name = arguments['--output']
    hd = df(arguments['<path>'], arguments['--quiet'], arguments['--like'])
    rhd = {k:v for k, v in hd.items() if len(v) > 1}
    fhd = pformat(rhd)
    if file_name:
        with open(file_name, 'w') as hf:
            hf.write(hd+'\n')
    else:
        print(fhd)
        if arguments['--size']:
            print(len(rhd))
    for dup in rhd.values():
        duplicates = list(dup)
        for i, file in enumerate(duplicates):
            print(f"{i} - {file}")
        try:
            to_delete = int(input())
            remove(duplicates[to_delete])
            print()
        except:
            pass
