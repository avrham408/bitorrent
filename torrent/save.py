from torrent.io import write_to_disc, open_file, close_file, create_file, get_path, copy_file, read_from_disk, make_dir, delete_file
from torrent.utilities import get_download_path, get_torrent_files_path
from torrent.torrent_file import generate_torrent_file
from torrent.pieces import create_piece_manager
import os
import logging
import asyncio


logger = logging.getLogger(__name__)

def make_env(): 
    handle_env_dirs(get_path('downloads'))
    handle_env_dirs(get_path('torrent_files'))
    logger.debug('env created')
        

def handle_env_dirs(dir_path):
    if not os.path.isdir(dir_path):
        if os.path.exists(dir_path):
            logger.info(f'{dir_path} is a file')
            delete_file(dir_path)
        make_dir(dir_path)

def create_single_file(torrent_name, torrent_size):
    path = get_download_path(torrent_name) 
    create_file(path, torrent_size) 


def save_torrent_file(src_path):
    dest_path = get_path('torrent_files')
    copy_file(src_path, dest_path)


def create_multi_file(torrent_file):
    torrent_dir_name = get_download_path(torrent_file.name)
    try:
        make_dir(torrent_dir_name)
    except FileExistsError:
        pass
    for file_data in torrent_file.files:
        create_file_and_file_path(torrent_dir_name, file_data)

def create_file_and_file_path(torrent_dir_name:str, file_data:dict):
    """
        the function get file_data that came from the torrent file
        the dict contain the length in bytes and all the path of the seprate in list.
        example : {'length': 353, 'path': [b'Other', b'Torrent Downloaded From ExtraTorrent.com.txt']}
        torrent_dir_name : is all the abs path of the torrent file dir in downloads directory
    """
    size = file_data['length']
    path = torrent_dir_name
    for pos in file_data['path'][:-1]:
        path = os.path.join(path, pos.decode())
        if not os.path.exists(path):
             make_dir(path)
    path = os.path.join(path, file_data['path'][-1].decode())
    create_file(path, size)

def file_genrator(torrent_file):
    save_torrent_file(torrent_file.path)
    if torrent_file.multi_file:
        create_multi_file(torrent_file)
    else:
        try:
            create_single_file(torrent_file.name, torrent_file.length)
        except OSError: # file size is 0
            return False
    logger.info('file created and torrent file saved')
    return True


async def write_pieces_to_memory(torrent_file, done_queue):
    if not torrent_file.multi_file:
        await handle_writing_to_single_file(torrent_file, done_queue)
    else:
        await handle_writing_to_multi_file(torrent_file, done_queue)
    logger.info("write pieces to memory closed") 


def write_piece_to_file(fd, piece, piece_size):
    try:
        write_to_disc(fd, piece.get_blocks(), (piece.index) * piece_size)
        piece.piece_written()
    except Exception:
        logger.error("write to disc failed", exc_info=True)
        return False
    return True


async def handle_writing_to_single_file(torrent_file, queue):
    fd = open_file(get_download_path(torrent_file.name))
    piece_size = torrent_file.piece_length
    logger.info(f"the fd num is {fd}")
    while True:
        piece = await queue.get()
        if not piece or not write_piece_to_file(fd, piece, piece_size): # push None in the queue to kill the proccess properly
            break
    close_file(fd)


def handle_writing_to_multi_file(torrent_file, queue):
    pass
    

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
    if os.path.isfile(file_path):
    #TODO seperate to functions
        fd = open_file(file_path)
        piece_manager = create_piece_manager(torrent_file)
        for piece in piece_manager.pieces:
            piece_data = read_piece(fd, piece)
            piece.add_block(piece_data)
            if piece.piece_done():
                piece.piece_written()
        close_file(fd)
        return torrent_file, piece_manager
    elif os.path.isdir(file_path):
        raise NotImplementedError('resume downloading multi file is not implmented')
    else:
        raise Exception("loading failed the torrent file name is not exist")


def torrent_file_exist(path:str):
    torrent_files_path = get_torrent_files_path(os.path.basename(path))
    return os.path.isfile(torrent_files_path)
