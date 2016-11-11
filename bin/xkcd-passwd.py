#!/usr/bin/env python3

import argparse
from random import sample


def main(words=3, separator='-'):
    with open('/usr/share/dict/words', 'r') as fobj:
        contents = fobj.read().split('\n')
        words = sample(contents, words)
        print(separator.join(words).title())

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate an xkcd password.')

    parser.add_argument('-w', '--words', dest='words', type=int, default=3,
                        help='How many words do you want in the password.')
    parser.add_argument('-s', '--separator', dest='separator', type=str,
                        default='-', help=("How would you like the words"
                                           "separated."))

    args = parser.parse_args()

    main(args.words, args.separator)
