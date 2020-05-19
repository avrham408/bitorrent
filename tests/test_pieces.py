from torrent.torrent_file import generate_torrent_file
from utilities import _files_list
from torrent.pieces import create_piece_manager, Piece, PieceStatus
import logging
import pytest
import asyncio

logger = logging.getLogger(__name__)

def test_create_piece_manager_pieces_size():
    files = _files_list()
    for torrent_path in files:
        torrent_file = generate_torrent_file(torrent_path)
        pieces_manager = create_piece_manager(torrent_file)
        size = 0
        for piece in pieces_manager.pieces:
            size += piece.length
        assert torrent_file.length == size


def test_create_piece_manager_all_pieces_available():
    files = _files_list()
    for torrent_path in files:
        torrent_file = generate_torrent_file(torrent_path)
        pieces_manager = create_piece_manager(torrent_file)
        ptr = 0
        for piece in pieces_manager.pieces:
            assert torrent_file.pieces[ptr:ptr+20] == piece.piece_hash
            ptr += 20


def test_create_piece_manager_last_piece():
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

    


@pytest.mark.asyncio
async def test_piece_manager_get_piece():
    files = _files_list()
    for torrent_path in files:
        torrent_file = generate_torrent_file(torrent_path)
        piece_manager = create_piece_manager(torrent_file)
        piece = await piece_manager.get_piece()
        assert type(piece) == Piece


@pytest.mark.asyncio
async def async_get_piece(piece_manager):
    for _ in range(5):
        piece = await piece_manager.get_piece()
        assert type(piece) == Piece
        assert piece.status == PieceStatus.in_progress
        await asyncio.sleep(1) 


@pytest.mark.asyncio
async def gathering(peer_manager):
    await asyncio.gather(*[async_get_piece(peer_manager) for _ in range(10)])


@pytest.mark.asyncio
async def test_get_piece_many_pieces_at_the_same_time():
    files = _files_list()
    for torrent_path in files:
        torrent_file = generate_torrent_file(torrent_path)
        piece_manager = create_piece_manager(torrent_file)
        await gathering(piece_manager)


if __name__ == "__main__":
    test_all_pieces_in_status()
