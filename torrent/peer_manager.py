from queue import Queue
from time import sleep
import logging

logger = logging.getLogger(__name__)

class Peer_manager():
    def __init__(self):
        self.peers = Queue()
        self.lock = False

    def add_peers(self, peers):
        if not self.lock:
            self.lock = True
            for peer in peers:
                self.peers.put(peer)
            self.lock = True
        else:
            logger.debug("add peers failed the peer_manager is lock")
            sleep(1)
            self.add_peers(peers)

