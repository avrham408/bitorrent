from torrent.networking import PeerConnection
from torrent.peer_protocol import Handshake, Keep_Alive, Interested, \
Unchoke, Choke, Piece, Request, BitField, Have

BLOCK_SIZE = 2**14

