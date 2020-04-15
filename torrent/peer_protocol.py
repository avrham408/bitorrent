import logging
import struct
from torrent.networking import open_connection, write, read

logger = logging.getLogger(__name__)
BLOCK_SIZE = 2**14
CONST_PROTOCOL = 'BitTorrent protocol'.encode('utf-8')


#out messages
def generate_keep_alive():
    return b'0000'


def generate_interested_message():
    return struct.pack('>IB', 1, 2)


def generate_handshake(info_hash, peer_id):
    peer_id = peer_id.encode('utf-8')
    return struct.pack('>B19s8x20s20s', 19, CONST_PROTOCOL, info_hash, peer_id)


def generate_request_message(piece_index, block_offset, block_size):
    return struct.pack('>IBIII', 13, 6, piece_index, block_offset, block_size)


#responses


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
    #empty
    if peer_response == b'':
        logger.debug('we got empty response')
    #keep alive
    elif len(peer_response) == 4 and peer_response == b'0000':
        return -1, 0
    #message type
    elif peer_response[4] in range(0,8):
        try:
            return struct.unpack(">IB", peer_response)
        except struct.error:
            logger.debug(f"unpack message type failed {peer_response}")
    return None, None


async def connect_peer(peer):
    peer_connection = await open_connection(*peer_connection.open_connection)
    if peer_connection is None:
        peer.close_connection()
        return False
    return True

def _get_have_positions(self, have_bytes):
    for byte in have_bytes:


"""
async def handshake(peer_connection):
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
    message_length , message_id = get_message_type(await reader.read(5))
    if message_id != 5:
        return False
    #TODO add support for saving bitfield data(the pieces that peer has)
    await reader.read(2048) #get all pieces avilable
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
        block_meta_data = await reader.read(8) #TODO valid [Piece Index| BLOCK OFFSET] == to request
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
"""    
    
        
class Message():
    message_id = None

    def send_bytes():
        return None

    @classmethod
    def parse():
        return None


class HandShake(Message):
    const_protocol = 'BitTorrent protocol'.encode('utf-8')
    message_id = None

    def __init__(self, info_hash, peer_id):
        self.info_hash = info_hash.encode('utf-8')
        self.peer_id = peer_id

    def send_bytes(self):
        try:
            return struct.pack('>B19s8x20s20s', 19, self.const_protocol, self.info_hash, self.peer_id)
        except struct.error as e:
            logger.error(exc_info=True)
            raise e

    @classmethod
    def parse(cls, data):
        try:
            _, _, info_hash, peer_id = struct.unpack(data)
        except struct.error:
            logger.debug("parse info hash failed")
            return None
        return cls(info_hash, peer_id)


class Keep_Alive(Message)
    message_id = None

    def __init__(self):
        pass

    def send_bytes(self):
        return b'0000'

    @classmethod
    def parse(cls, data):
        struct.unpack(">IB", data)
        if data == b'0000':
            return cls()
        return None

class Choke(Message):
    message_id = 1
    def __init__(self):
        pass

    def send_bytes(self):
        return struct.pack('>IB' , 1, self.message_id)

    @classmethod
    def parse(cls, data):
        size, message_id = struct.unpack(">IB", peer_response)
        if message_id == self.message_id: 
            return cls()
        return None

class Unchoke(Message):
    message_id = 1
    def __init__(self):
        pass

    def send_bytes(self):
        return struct.pack('>IB' , 1, self.message_id)


    @classmethod
    def parse(cls, data):
        size, message_id = struct.unpack(">IB", peer_response)
        if message_id == self.message_id: 
            return cls()
        return None

class Interested(Message):
    message_id = 2
    def __init__(self):
        pass

    def send_bytes(self):
        return struct.pack('>IB' , 1, self.message_id)

    @classmethod
    def parse(cls, data):
        size, message_id = struct.unpack(">IB", peer_response)
        if message_id == self.message_id: 
            return cls()
        return None

class Uninterested(Message):
    message_id = 3
    def __init__(self):
        pass

    def send_bytes(self):
        return struct.pack('>IB' , 1, self.message_id)

    @classmethod
    def parse(cls, data):
        size, message_id = struct.unpack(">IB", peer_response)
        if message_id == self.message_id: 
            return cls()
        return None

class Have(Message):
    message_id = 4
    def __init__(self, piece_index):
        self.piece_index = piece_index
        

    def send_bytes(self):
        return b'0000'

    @classmethod
    def parse(cls, data):
        size, message_id, piece_index  = struct.unpack(">IBI", peer_response)
        if message_id == self.message_id: 
            return cls(piece_index)
        return None


class BitField(Message):
    message_id = 5
    def __init__(self, have_position_genrator):
        self.position_genrator = have_position_genrator

    def send_bytes(self):
        return b'0000'


    @classmethod
    def parse(cls, data):
        size, message_id = struct.unpack(">IB", peer_response[0:5])
        if message_id == self.message_id: 
            
            return cls(piece_index)
        return None
    

 5 - bitfield (what i got my brother)
 6 - request
 7 - piece
 8 - cancel

if __name__ == "__main__":

