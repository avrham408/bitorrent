import sys, getopt
import os
from torrent.client import create_client, run_client, close_client

def main(argv):
    if len(argv) != 1:
        print("usage: main.py <torrent file>")
    elif os.path.splitext(argv[0])[-1] != '.torrent':
        print("the file is not torrent file")
        print("usage: main.py <torrent file>")
    else:
        torrent_file, piece_manager, tracker_threads, peer_manager, loop = create_client(argv[0])
        try:
            loop.run_until_complete(run_client(torrent_file, piece_manager, tracker_threads, peer_manager, loop))
        except KeyboardInterrupt:
            loop.run_until_complete(close_client(loop, tracker_threads, piece_manager))


if __name__ == "__main__":
   main(sys.argv[1:])
