from torrent.io import write_to_disc, open_file, close_file, create_file, get_path, copy_file, read_from_disk
from torrent.utilities import get_download_path, get_torrent_files_path
from torrent.torrent_file import generate_torrent_file
from torrent.pieces import create_piece_manager
import os
import logging
import asyncio


logger = logging.getLogger(__name__)

def create_single_file(torrent_name, torrent_size):
    path = get_download_path(torrent_name) 
    create_file(path, torrent_size) 


def save_torrent_file(src_path):
    dest_path = get_path('torrent_files')
    copy_file(src_path, dest_path)


def file_genrator(torrent_file):
    save_torrent_file(torrent_file.path)
    if torrent_file.multi_file:
        raise NotImplementedError("clinet not support multi file torrent")
    else:
        try:
            create_single_file(torrent_file.name, torrent_file.length)
        except OSError: # file size is 0
            return False
    logger.info('file created and torrent file saved')
    return True


async def write_pieces_to_memory(torrent_file, done_queue):
    fd = open_file(get_download_path(torrent_file.name))
    piece_size = torrent_file.piece_length
    logger.info(f"the fd num is {fd}")
    while True:
        piece = await done_queue.get()
        if not piece:
            break
        logger.debug(f'piece {piece.index} get to write pieces')
        try:
            write_to_disc(fd, piece.get_blocks(), (piece.index) * piece_size)
            piece.piece_written()
        except Exception:
            logger.error("write to disc failed", exc_info=True)
            return False
        torrent_file
    close_file(fd)
    logger.info("write pieces to memory closed") 


def load_torrent_file(path):
    if os.path.isfile(path):
        return generate_torrent_file(path)


def read_piece(fd, piece):
    return read_from_disk(fd, piece.length)


def load(torrent_path):
    torrent_file = load_torrent_file(torrent_path)
    if not torrent_file:
        return False
    file_path = get_download_path(torrent_file.name)
    fd = open_file(file_path)
    piece_manager = create_piece_manager(torrent_file)
    for piece in piece_manager.pieces:
        piece_data = read_piece(fd, piece)
        piece.add_block(piece_data)
        if piece.piece_done():
            piece.piece_written()
    close_file(fd)
    return torrent_file, piece_manager


def torrent_file_exist(path:str):
    torrent_files_path = get_torrent_files_path(os.path.basename(path))
    return os.path.isfile(torrent_files_path)
