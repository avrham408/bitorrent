from torrent.torrent_file import generate_torrent_file
from torrent.pieces import create_piece_manager
from torrent.peer import Peer_manager
from torrent.tracker import tracker_manager
from torrent.peer_communication import peer_to_peer_communication
from torrent.save import torrent_file_exist, load, write_pieces_to_memory, file_genrator, make_env
from torrent.async_handler import get_loop, run_async_task
from torrent.utilities import close_thread
from torrent.status_interface import run_tqdm
import asyncio
import logging


logger = logging.getLogger(__name__)
MAX_PEERS = 50
SLEEP_BETWEEN_LOOP = 3




def create_or_load_torrent_file(path:str):
    make_env()
    if torrent_file_exist(path):
        try:
            torrent_file, piece_manager = load(path)
        except TypeError:
            raise Exception("loading torrent file failed")
    else:
        torrent_file = generate_torrent_file(path) 
        file_genrator(torrent_file)
        piece_manager= create_piece_manager(torrent_file) 
    return torrent_file, piece_manager


async def close_client(loop, tracker_threads, piece_manager):
    await piece_manager.put_in_queue(None)
    for thread in tracker_threads:
        close_thread(thread)
    logger.info("proccess closed successfuly")
    loop.stop()


def create_client(torrent_path:str):
    loop = get_loop()
    torrent_file, piece_manager = create_or_load_torrent_file(torrent_path)
    run_async_task(loop, write_pieces_to_memory(torrent_file, piece_manager.done_queue))
    peer_manager = Peer_manager()
    tracker_threads = tracker_manager(torrent_file, peer_manager)
    return torrent_file, piece_manager, tracker_threads, peer_manager, loop


async def run_client(torrent_file, piece_manager, tracker_threads, peer_manager, loop):
    timeing = 0
    run_async_task(loop, run_tqdm(torrent_file.length, torrent_file.piece_length, piece_manager.get_pieces_written))
    while True:
        timeing += 1 
        if MAX_PEERS > peer_manager.map_status()['in_progress'] and not peer_manager.peers.empty():
            task = peer_to_peer_communication(peer_manager.get_peer(), torrent_file, piece_manager)
            run_async_task(loop, task)
        if piece_manager.all_pieces_done():
            logger.info("all pieces done")
            await close_client(loop, tracker_threads, piece_manager)
            break
        await asyncio.sleep(SLEEP_BETWEEN_LOOP)
