from torrent.save import write_pieces_to_memory, file_genrator
from torrent.torrent_file import generate_torrent_file
from torrent.pieces import create_piece_manager, PieceStatus
import torrent
import pytest
import asyncio
import struct 
from utilities import _files_list
import logging 
import os

logger = logging.getLogger(__name__)


# help functions
def delete_file_for_test_if_exsit(torrent_file):
    base_path = os.path.dirname(torrent.__path__[0])
    path_torrent_file = os.path.join(base_path, 'torrent_files', os.path.basename(torrent_file.path))
    path_download_file = os.path.join(base_path, 'downloads', torrent_file.name)
    try:
        os.remove(path_torrent_file)
    except FileNotFoundError:
        pass
    try:
        os.remove(path_download_file)
    except FileNotFoundError:
        pass
        

def create_test_data_for_piece(piece):
    return struct.pack('>B', piece.index % 255) * piece.length 


def full_piece_with_bytes(piece):
    data = create_test_data_for_piece(piece)
    for _ in range(int(piece.length / (2 ** 14))):
        piece.add_block(data)
    piece.status = PieceStatus.done


# tests

def check_all_data_wirtten_in_right_place(torrent_file, piece_manager):
    base_path = os.path.dirname(torrent.__path__[0])
    path_download_file = os.path.join(base_path, 'downloads', torrent_file.name)
    assert os.stat(path_download_file).st_size  == torrent_file.length
    with open(path_download_file, 'rb') as f:
        for piece in piece_manager.pieces:
            f.read(piece.length) == create_test_data_for_piece(piece)


@pytest.mark.asyncio
async def test_write_file():
    path = _files_list()[3] #only not multi file in _file_list
    torrent_file = generate_torrent_file(path)
    file_genrator(torrent_file)
    delete_file_for_test_if_exsit(torrent_file)
    file_genrator(torrent_file)
    piece_manager = create_piece_manager(torrent_file)
    asyncio.gather(write_pieces_to_memory(torrent_file, piece_manager.done_queue))
    for piece in piece_manager.pieces:
        full_piece_with_bytes(piece)
        await piece_manager.put_in_queue(piece)
        piece.piece_written()
    await piece_manager.done_queue.put(None)
    check_all_data_wirtten_in_right_place(torrent_file, piece_manager)
    #close process
    delete_file_for_test_if_exsit(torrent_file)
