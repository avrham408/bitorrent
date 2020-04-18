import asyncio
import struct
import logging

logger = logging.getLogger(__name__)
BLOCK_SIZE = 2**14
CONST_PROTOCOL = 'BitTorrent protocol'.encode('utf-8')


###### out messages ######

def generate_keep_alive():
    return b'0000'


def generate_interested_message():
    return struct.pack('>IB', 1, 2)


def generate_handshake(info_hash, peer_id):
    peer_id = peer_id.encode('utf-8')
    return struct.pack('>B19s8x20s20s', 19, CONST_PROTOCOL, info_hash, peer_id)


def generate_request_message(piece_index, block_offset, block_size):
    return struct.pack('>IBIII', 13, 6, piece_index, block_offset, block_size)


###### Responses ######

def valid_res_hand_shake(res):
    try:
        num, protocol, _, _ = struct.unpack('>B19s8x20s20s', res)
    except struct.error:
        logger.debug("message got empty")
        return False
    if num != 19 and protocl == CONST_PROTOCOL:
        logger.warning('you didnt got handshake')
        return False
    return True


def get_message_type(peer_response):
    """
        False empty
       -1 - keep alive
        0 - choke
        1 - unchoke
        2 - interested
        3 - uninterested
        4 - have
        5 - bitfield (what i got my brother)
        6 - request
        7 - piece
        8 - cancel
    """
    # empty
    if peer_response == b'':
        logger.debug('we got empty response')
    # keep alive
    elif len(peer_response) == 4 and peer_response == b'0000':
        return -1, 0
    # message type
    elif peer_response[4] in range(0, 8):
        try:
            return struct.unpack(">IB", peer_response)
        except struct.error:
            logger.debug(f"unpack message type failed {peer_response}")
    return None, None


async def peer_connection(peer, torrent_file, piece_manager):
    try:
        reader, writer = await asyncio.open_connection(peer.ip, peer.port)
    except OSError:
        logger.debug("connection call failed")
        return False
    logger.debug(f'{peer} connection opend')
    if not await handshake(reader, writer, torrent_file):
        logger.debug("connection failed")
        return False
    logger.debug(f"{peer} -  handshake sent")
    if not await bitfield(reader, peer):
        logger.debug(f"{peer} - bitfield failed")
    logger.debug(f"{peer} - bitfiled success")
    message_id = await intersted(reader, writer)
    if message_id is None or message_id not in (0, 1):
        logger.debug(f"{peer} - intersted request failed")
        return False
    elif message_id == 0:
        # TODO support recursion for choke
        logger.debug(f"{peer} - choked")
        return False
    logger.debug(f"{peer} - unchoke")
    while True:
        piece = await piece_manager.get_piece()
        if piece:
            block_status = await request_block(piece, reader, writer, peer)
            if not block_status:
                # TODO sleep and recursion
                logger.debug("block request failed")
                piece.reset_piece()
            piece.piece_done()
        else:
            logger.debug(f"{peer} did'nt get piece and connection closed")
            return True


async def request_block(piece, reader, writer, peer):
    offset = 0
    while offset < piece.length:
        request_message = generate_request_message(piece.index, offset, BLOCK_SIZE)
        writer.write(request_message)
        await writer.drain()

        request_response = await reader.read(5)
        size, message_id = get_message_type(request_response)
        if not message_id:
            return False
        if message_id != 7:
            logger.debug(f"{peer}we got from peer {message_id} message id for reques piece")
            return False
        if size - 9 != BLOCK_SIZE:
            logger.debug(f"{peer} the block size is not on the size we asked")
        logger.debug("starting scrap block")
        block_meta_data = await reader.read(8)  # TODO valid [Piece Index| BLOCK OFFSET] == to request
        block = await read_all_block(reader, size - 9)
        if block:
            offset += size - 9
            piece.add_block(block)
        else:
            return False
    logger.debug("block scrap successfuly")
    return True


async def read_all_block(reader, size):
    block = b''
    while True:
        chunk = await reader.read(size)
        block += chunk
        if len(block) >= size:
            return block[:size]
        elif chunk == b'':
            logger.info("chunk of block got empty")
            return False


async def handshake(reader, writer, torrent_file):
    handshake_message = generate_handshake(torrent_file.info_hash, torrent_file.peer_id)
    writer.write(handshake_message)
    await writer.drain()
    try:
        handshake_res = await reader.read(68)
    except ConnectionResetError:
        logger.debug("connection with peer end")
        return False
    return valid_res_hand_shake(handshake_res)


async def bitfield(reader, peer):
    message_length, message_id = get_message_type(await reader.read(5))
    if message_id != 5:
        return False
    # TODO add support for saving bitfield data(the pieces that peer has)
    await reader.read(2048)  # get all pieces avilable
    return True


async def intersted(reader, writer):
    interested_message = generate_interested_message()
    writer.write(interested_message)
    await writer.drain()
    try:
        interested_res = await reader.read(5)
    except ConnectionResetError:
        logger.debug("connection with peer end")
        return False
    _, choke_status = get_message_type(interested_res)
    return choke_status
