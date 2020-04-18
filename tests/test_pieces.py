from torrent.torrent_file import generate_torrent_file
from utilities import _files_list
from torrent.pieces import create_piece_manager
import logging

logger = logging.getLogger(__name__)

def test_create_pieces_manager_pieces_size():
    files = _files_list()
    for torrent_path in files:
        torrent_file = generate_torrent_file(torrent_path)
        pieces_manager = create_piece_manager(torrent_file)
        size = 0
        for piece in pieces_manager.pieces:
            size += piece.length
        assert torrent_file.length == size


def test_create_pieces_manager_all_pieces_available():
    files = _files_list()
    for torrent_path in files:
        torrent_file = generate_torrent_file(torrent_path)
        pieces_manager = create_piece_manager(torrent_file)
        ptr = 0
        for piece in pieces_manager.pieces:
            assert torrent_file.pieces[ptr:ptr+20] == piece.piece_hash
            ptr += 20

def test_create_pieces_manager_last_piece():
    files = _files_list()
    for torrent_path in files:
        torrent_file = generate_torrent_file(torrent_path)
        piece_manager = create_piece_manager(torrent_file)
        last_piece = piece_manager.pieces[len(piece_manager.pieces) - 1]
        assert torrent_file.length % torrent_file.piece_length == last_piece.length

def test_all_pieces_in_status():
    files = _files_list()
    for torrent_path in files:
        torrent_file = generate_torrent_file(torrent_path)
        piece_manager = create_piece_manager(torrent_file)
        status_dict = piece_manager.pieces_status()
        assert len(piece_manager.pieces) == sum([i for i in status_dict.values()])

    


if __name__ == "__main__":
    test_all_pieces_in_status()
