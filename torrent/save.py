from torrent.io import write_to_disc, open_file, close_file, create_file, get_path, copy_file
from torrent.utilities import get_download_path 
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


def load_from_memory(torrent_file):
    pass


async def write_pieces_to_memory(torrent_file, done_queue):
    fd = open_file(get_download_path(torrent_file.name))
    piece_size = torrent_file.piece_length
    logger.info(f"the fd num is {fd}")
    while True:
        piece = await done_queue.get()
        if not piece:
            break
        logger.info(f'piece {piece.index} get to write pieces')
        try:
            write_to_disc(fd, piece.get_blocks(), (piece.index) * piece_size)
            piece.piece_written()
        except Exception:
            logger.error("write to disc failed", exc_info=True)
            return False
    close_file(fd)
    logger.info("write pieces to memory closed") 
