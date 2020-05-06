from torrent.networking import PeerConnection
from torrent.peer_protocol import Handshake, Keep_Alive, Interested, \
    Unchoke, Choke, Piece, Request, BitField, Have, Uninterested, Cancel
import logging
import asyncio
import struct

BLOCK_SIZE = 2**14
logger = logging.getLogger(__name__)
RESTART_PEER_TIME = 60 * 7.5


async def read_message(peer_connection):
    pack = await peer_connection.read(5)
    if not pack:
        return False
    if len(pack) == 4:
        return Keep_Alive()
    try:
        message_size, message_type = struct.unpack(">IB", pack)
    except struct.error:
        logger.info("parse message and size failed")
        return False
    if message_size > 1:
        try:
            pack += await peer_connection.read(message_size - 1, all_data=True)
        except TypeError:
            return False
    return message_type_switch(message_type).parse(pack)


def message_type_switch(message_type):
    if message_type == 0:
        return Choke
    if message_type == 1:
        return Unchoke
    if message_type == 2:
        return Interested
    if message_type == 3:
        return Uninterested
    if message_type == 4:
        return Have
    if message_type == 5:
        return BitField
    if message_type == 6:
        return Request
    if message_type == 7:
        return Piece
    if message_type == 8:
        return Cancel


async def open_connection(peer):
    peer_connection = await PeerConnection.open_connection(*peer.open_connection())
    if not peer_connection:
        return False
    return peer_connection


def create_handshake(info_hash, peer_id):
    return Handshake(info_hash, peer_id)


async def send_handshake(peer_connection, handshake):
    if await peer_connection.write(handshake.send_bytes()):
        return True
    return False


async def get_and_parse_handshake(peer_connection, recursive=True):
    res = await peer_connection.read(68, all_data=True)
    if res:
        return Handshake.parse(res)
    elif recursive is True:
        await asyncio.sleep(10)
        return await get_and_parse_handshake(peer_connection, False)



async def get_and_parse_bitfield(peer_connection):
    # TODO handle Have messages
    bitfield = await read_message(peer_connection)
    if type(bitfield) != BitField:
        logger.debug(f"we got from peer in bitfield {bitfield}")
        return False
    else:
        return bitfield


async def send_intersted(peer_connection):
    intersted = Interested()
    if await peer_connection.write(intersted.send_bytes()):
        return True
    return False


async def get_choking_status(peer_connection):
    status = await read_message(peer_connection)
    if type(status) == Choke:
        # TODO handle restart peer communication
        logger.debug("peer choke")
        await asyncio.sleep(RESTART_PEER_TIME)
        return False
    if type(status) == Unchoke:
        return True
    return False


async def get_pieces(peer_connection, piece_manager, bitfield):
    while True:
        piece = await piece_manager.get_piece()
        if not piece:
            # all the pieces in proccess
            return False
        await request_all_blocks_for_piece(peer_connection, piece)
        if not piece.piece_done():
            # TODO handle restart
            logger.info("piece requests from peer failed")
            return False
        await piece_manager.put_in_queue(piece)
        logger.debug('piece add to queue')


async def request_all_blocks_for_piece(peer_connection, piece):
    offset = 0
    while offset < piece.length:
        if not await request_piece(peer_connection, piece.index, offset, BLOCK_SIZE):
            return False
        piece_message = await read_message(peer_connection)
        if type(piece_message) is not Piece:
            return False
        piece.add_block(piece_message.block_data)
        offset += len(piece_message.block_data)


async def request_piece(peer_connection, piece_index, offset, block_size):
    request_message = Request(piece_index, offset, block_size)
    if await peer_connection.write(request_message.send_bytes()):
        return True
    return False


def close_connection(peer):
    peer.close_connection()
    return False


async def restart(peer, torrent_file, piece_manager):
    return await peer_to_peer_communication(peer, torrent_file, piece_manager)


async def peer_to_peer_communication(peer, torrent_file, piece_manager):
    peer_connection = await open_connection(peer)
    if not peer_connection:
        logger.info("open connections failed")
        return close_connection(peer)
    logger.debug("connection open")
    handshake = create_handshake(torrent_file.info_hash, torrent_file.peer_id)
    if not await send_handshake(peer_connection, handshake):
        logger.info("send handshake failed")
        return close_connection(peer)
    logger.debug("handshake pass")
    if not await get_and_parse_handshake(peer_connection):
        logger.info("res handshake failed")
        return close_connection(peer)
    bitfield = await get_and_parse_bitfield(peer_connection)
    if not bitfield:
        logger.info("bitfield failed")
        return close_connection(peer)
    logger.debug("bitfield pass")
    if not await send_intersted(peer_connection):
        logger.info("send intersted message failed")
        return close_connection(peer)
    logger.debug("send interested pass")
    if not await get_choking_status(peer_connection):
        logger.info("peer choking status return False")
        return close_connection(peer)
    logger.debug("get choke status pass")
    if not await get_pieces(peer_connection, piece_manager, bitfield):
        return close_connection(peer)
    logger.debug("get choke status pass")
