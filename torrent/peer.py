from queue import Queue
from time import sleep
import socket
import logging
from enum import Enum


logger = logging.getLogger(__name__)


class PeerStatus(Enum):
    free = 0
    in_progress = 1
    failed = 2


class Peer_manager():
    def __init__(self):
        self.peers = Queue()
        self.peer_list = []
        self.lock = False

    def add_peers(self, peers):
        if not self.lock:
            self.lock = True
            for peer_data in peers:
                # TODO add support for duplicate peers
                if _valid_peer(peer_data[0], peer_data[1]):
                    peer = Peer(peer_data[0], peer_data[1])
                    if peer not in self.peer_list:
                        self.peers.put(peer)
                        self.peer_list.append(peer)
                    else:
                        logging.debug("duplicate peer")
                else:
                    logging.debug("peer not valid")
            self.lock = False
        else:
            logger.debug("add peers failed the peer_manager is lock")
            sleep(5)
            self.add_peers(peers)

    def get_peer(self):
        if not self.lock:
            self.lock = True
            if not self.peers.empty():
                peer = self.peers.get()
                self.lock = False
                return peer
            self.lock = False

    def map_status(self):
        statuses = list(map(lambda peer: peer.status, self.peer_list))
        statuses_dic = dict()
        statuses_dic[PeerStatus.free.name] = statuses.count(PeerStatus.free)
        statuses_dic[PeerStatus.in_progress.name] = statuses.count(PeerStatus.in_progress)
        statuses_dic[PeerStatus.failed.name] = statuses.count(PeerStatus.failed)
        return statuses_dic


class Peer:
    def __init__(self, ip, port):
        self.port = port
        self.ip = ip
        self.status = PeerStatus.free

    def open_connection(self):
        self.status = PeerStatus.in_progress
        return self.ip, self.port

    def close_connection(self):
        # True is torrent done and False is connection problem
        self.status = PeerStatus.failed

    def __hash__(self):
        return hash((self.port, self.ip))

    def __eq__(self, other):
        return (self.__class__ == other.__class__
                and self.ip == other.ip
                and self.port == other.port)

    def __ne__(self, other):
        return not self.__eq__(self, other)

    def __repr__(self):
        return f"{self.ip}:{self.port}:{self.status.name}"


def _valid_peer(ip, port):
    try:
        socket.inet_aton(ip)
    except socket.error:
        return False
    if not 1 <= port <= 65535:
        return False
    return True
