from queue import Queue
from time import sleep
import logging

logger = logging.getLogger(__name__)

class Peer_manager():
    def __init__(self):
        self.peers = Queue()
        self.l = []
        self.lock = False

    def add_peers(self, peers):
        if not self.lock:
            self.lock = True
            for peer in peers:
                self.peers.put(peer)
                self.l.append(peer)
            self.lock = False 
        else:
            logger.debug("add peers failed the peer_manager is lock")
            sleep(5)
            self.add_peers(peers)

