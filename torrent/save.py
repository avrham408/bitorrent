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
        create_single_file(torrent_file.name, torrent_file.length)
    logger.info('file created and torrent file saved')
    return True


async def write_pieces_to_memory(torrent_file, piece_manager):
    if torrent_file.multi_file:
        await handle_writing_to_multi_file(torrent_file, piece_manager)
    else:
        await handle_writing_to_single_file(torrent_file, piece_manager.done_queue)
    logger.info("write pieces to memory closed") 


async def handle_writing_to_multi_file(torrent_file, piece_manager):
    pieces_positions_in_files = create_map_for_pieces(torrent_file.files, piece_manager.pieces)
    while True:
        logger.info("wating for piece")
        piece = await piece_manager.done_queue.get()
        if not piece:
            break
        files_list = pieces_positions_in_files[piece]
        if not write_piece_to_multi_files(piece, files_list, torrent_file.name):
            break
            

def parse_and_get_abs_path(torrent_dir, undecode_postions_list):
    base_path = os.path.join(*[pos_name.decode() for pos_name in undecode_postions_list])
    base_path = os.path.join(torrent_dir, base_path)
    return get_download_path(base_path)


def write_piece_to_multi_files(piece, files_list, torrent_dir_name):
    piece_data = piece.get_blocks()
    seek_in_piece = 0
    ans = []
    for file_data in files_list:
        abs_path = parse_and_get_abs_path(torrent_dir_name, file_data[0])
        fd = open_file(abs_path)
        try:
            write_to_disc(fd, piece_data[seek_in_piece: seek_in_piece + file_data[2]],file_data[1])
        except Exception:
            close_file(fd)
            logger.error("write to disc failed", exc_info=True)
            return False
        seek_in_piece += file_data[2]
        close_file(fd)
    piece.piece_written()
    return True


def create_map_for_pieces(files:list, pieces:list): 
    positions_map = dict()
    files_gen = (file_in_torrent for file_in_torrent in files) #genrator of files
    file_data = next(files_gen)
    current_seek_in_current_file = 0
    for piece in pieces:
        positions_map[piece] = []
        current_seek_in_piece = 0
        while True:
            if piece.length - current_seek_in_piece > file_data['length'] - current_seek_in_current_file:
                current_seek_in_piece += file_data['length'] - current_seek_in_current_file 
                bytes_size_to_write_on_file = file_data['length'] - current_seek_in_current_file
                positions_map[piece].append([file_data['path'], current_seek_in_current_file, bytes_size_to_write_on_file]) 
                #moving_to_the_next_file
                file_data = next(files_gen)
                current_seek_in_current_file = 0
            else:
                positions_map[piece].append([file_data['path'], current_seek_in_current_file , piece.length - current_seek_in_piece])
                current_seek_in_current_file += piece.length - current_seek_in_piece
                break
    return positions_map


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
            close_file(fd)
            break 

def load_torrent_file(path):
    if os.path.isfile(path):
        return generate_torrent_file(path)


def read_piece(fd, piece):
    return read_from_disk(fd, piece.length)


def load(torrent_path):
    torrent_file = load_torrent_file(torrent_path)
    piece_manager = create_piece_manager(torrent_file)
    if not torrent_file:
        return False
    download_path = get_download_path(torrent_file.name)
    if os.path.isfile(download_path):
        load_single_file(download_path, piece_manager)
    elif os.path.isdir(download_path):
        load_multi_file(download_path, piece_manager, torrent_file)
    else:
        raise Exception("loading failed the torrent file name is not exist")
    return torrent_file, piece_manager


def load_single_file(file_path, piece_manager):
    fd = open_file(file_path)
    for piece in piece_manager.pieces:
        piece_data = read_piece(fd, piece)
        piece.add_block(piece_data)
        if piece.piece_done():
            piece.piece_written()
    close_file(fd)


def load_multi_file(dir_path, piece_manager, torrent_file):
    pieces_positions_in_files  = create_map_for_pieces(torrent_file.files, piece_manager.pieces)
    for piece, files_data in pieces_positions_in_files.items():
        for file_data in files_data:
            read_piece_for_multi_file(file_data, piece, dir_path)
        if piece.piece_done():
            piece.piece_written()

def read_piece_for_multi_file(file_data, piece, dir_path):
    file_path, seek_position, size = file_data
    abs_path = parse_and_get_abs_path(dir_path, file_path)
    fd = open_file(abs_path)
    block_of_data = read_from_disk(fd, size, seek_position)
    piece.add_block(block_of_data)
    close_file(fd)


def torrent_file_exist(path:str):
    torrent_files_path = get_torrent_files_path(os.path.basename(path))
    return os.path.isfile(torrent_files_path)
