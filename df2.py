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
def md5_hash(file_path: str) -> str:
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

def duplicate_finder(paths: list, quiet: bool, like: str) -> dict:
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
            if not quiet:
                print(directory_path)
            files = directory[2]
            for f in files:
                h = md5_hash(join(directory_path,f))
                hash_dict[h].add(join(directory_path,f))
    if like:
        return {like_hash: hash_dict[like_hash]}
    return hash_dict

def main():
    """
    Take any number of paths received as arg and write the path of every file that has a duplicate
    """
    arguments = docopt(__doc__)
    output_filename = arguments['--output']
    hash_dict = duplicate_finder(arguments['<path>'], arguments['--quiet'], arguments['--like'])
    raw_hash_dict = {k:v for k, v in hash_dict.items() if len(v) > 1}
    formated_hash_dict = pformat(raw_hash_dict)
    if output_filename:
        with open(output_filename, 'w') as output_file:
            output_file.write(hash_dict+'\n')
    else:
        print(formated_hash_dict)
        if arguments['--size']:
            print(len(raw_hash_dict))
    for dup in raw_hash_dict.values():
        duplicates = list(dup)
        for i, file in enumerate(duplicates):
            print(f"{i} - {file}")
        try:
            to_delete = int(input())
            remove(duplicates[to_delete])
            print()
        except:
            pass

if __name__ == '__main__':
    main()
