
import sys
import time

def parse_from_root(args):
    print(f'LegacyMan parser running, with these arguments: {args}')
    start_time = time.time()
    #Parse the document...
    end_time = time.time()
    parse_time = end_time - start_time
    print(f'Parse complete after {parse_time} seconds')

if __name__ == '__main__':
    args = sys.argv[1:]
    parse_from_root(args)