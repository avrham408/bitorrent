from torrent.networking import generate_keep_alive, generate_interested_message, generate_handshake
from torrent.torrent_file import generate_torrent_file

from utilities import valid_internet, _files_list, kill_thread
import struct


def test_generate_keep_alive():
    assert generate_keep_alive() == b'0000'


def test_generate_intersted_message():
    assert generate_interested_message() == b'\x00\x00\x00\x01\x02'


def test_generate_handshake():
    files = _files_list()
    for torrent_file in files:
        torrent_file = generate_torrent_file(torrent_file)
        const_protocol = 'BitTorrent protocol'.encode('utf-8')
        peer_id = torrent_file.peer_id.encode('utf-8')
        packet = struct.pack('>B19s8x20s20s', 19, const_protocol, torrent_file.info_hash, peer_id)
        assert packet == generate_handshake(torrent_file.info_hash, torrent_file.peer_id) 


if __name__ == "__main__":
    test_handshake()
    
