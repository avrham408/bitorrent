from torrent.torrent_file import generate_torrent_file
from torrent.pieces import create_piece_manager
from torrent.peer import Peer_manager
from torrent.tracker import tracker_manager
from torrent.peer_communication import gather_peers
import logging

logger = getLogger(__name__)



def main_loop(torrent_path:str):
    torrent_file = generate_torrent_file(torrent_path) 
    piece_manager= create_piece_manager(torrent_file)
    peer_manager = Peer_manager()
    tracker_threads = tracker_manager(torrent_file, peer_manager)
    while True:
        if peer_manager.peers.empty() is False:
            gather_peers(peer_manager, piece_manager, torrent_file)
        await 

            
if __name__ == "__main__":
    path = ''
    main_loop(path)

