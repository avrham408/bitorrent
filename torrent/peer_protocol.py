"""Peer Protocol contain 10 types of messages:
    Handshake - no message type
    Keep_Alive - no message_type
    Choke - 0
    Unchoke - 1
    Interested - 2
    uninterested - 3
    have - 4
    BitField - 5
    Request - 6
    Piece - 7
    Cancel - 8
   The file contain the implmentaion in oop of every class and data that belong to him
"""
import logging
import struct
from bitarray import bitarray

logger = logging.getLogger(__name__)


class Message():
    message_id = None

    def send_bytes():
        return None

    @classmethod
    def parse():
        return None


class Handshake(Message):
    const_protocol = 'BitTorrent protocol'.encode('utf-8')
    message_id = None

    def __init__(self, info_hash: bytes, peer_id: str):
        self.info_hash = info_hash
        self.peer_id = self._encode_peer_id(peer_id)

    def send_bytes(self):
        return struct.pack('>B19s8x20s20s', 19, self.const_protocol, self.info_hash, self.peer_id)

    def _encode_peer_id(self, peer_id):
        try:
            return peer_id.encode('utf-8')
        except AttributeError:
            return peer_id

    @classmethod
    def parse(cls, data):
        try:
            _, _, info_hash, peer_id = struct.unpack('>B19s8x20s20s', data)
        except struct.error:
            logger.debug("parse info hash failed")
            return None
        return cls(info_hash, peer_id)


class Keep_Alive(Message):
    message_id = None

    def send_bytes(self):
        return b'0000'

    @classmethod
    def parse(cls, data):
        struct.unpack(">IB", data)
        if data == b'0000':
            return cls()
        return None


class Choke(Message):
    message_id = 0

    def send_bytes(self):
        return struct.pack('>IB', 1, self.message_id)

    @classmethod
    def parse(cls, data):
        # data = b'00011
        size, message_id = struct.unpack(">IB", data)
        if message_id == cls.message_id:
            return cls()
        return None


class Unchoke(Message):
    message_id = 1

    def send_bytes(self):
        return struct.pack('>IB', 1, self.message_id)

    @classmethod
    def parse(cls, data):
        # data = b'00010
        size, message_id = struct.unpack(">IB", data)
        if message_id == cls.message_id:
            return cls()
        return None


class Interested(Message):
    message_id = 2

    def send_bytes(self):
        return struct.pack('>IB', 1, self.message_id)

    @classmethod
    def parse(cls, data):
        # data = b'00012
        size, message_id = struct.unpack(">IB", data)
        if message_id == cls.message_id:
            return cls()
        return None


class Uninterested(Message):
    message_id = 3

    def send_bytes(self):
        return struct.pack('>IB', 1, self.message_id)

    @classmethod
    def parse(cls, data):
        size, message_id = struct.unpack(">IB", peer_response)
        if message_id == cls.message_id:
            return cls()
        return None


class Have(Message):
    message_id = 4

    def __init__(self, piece_index):
        self.piece_index = piece_index

    def send_bytes(self):
        raise NotImplementedError("The app doesn't support sending Have messages")

    @classmethod
    def parse(cls, data):
        size, message_id, piece_index = struct.unpack(">IBI", data)
        if message_id == cls.message_id:
            return cls(piece_index)
        return None


class BitField(Message):
    message_id = 5

    def __init__(self, positions):
        self.available_positions = positions

    def send_bytes(self):
        # TODO add support for seeding
        raise NotImplementedError("The app doesn't support sending BitField messages")

    @classmethod
    def _parse_bitfield(self, hex_data):
        bits = bitarray()
        bits.frombytes(hex_data)
        return bits

    @classmethod
    def parse(cls, data):
        size, message_id = struct.unpack(">IB", data[0:5])
        if message_id == cls.message_id:
            positions = cls._parse_bitfield(data[5:size + 4])
            return cls(positions)
        return None


class Request(Message):
    message_id = 6

    def __init__(self, piece_index, block_offset, block_length):
        self.piece_index = piece_index
        self.block_offset = block_offset
        self.block_length = block_length

    def send_bytes(self):
        return struct.pack('>IBIII', 13, self.message_id, self.piece_index, self.block_offset, self.block_length)

    @classmethod
    def parse(cls):
        # TODO add support for seeding
        raise NotImplementedError("The app doesn't support sending Request messages")


class Piece(Message):
    message_id = 7

    def __init__(self, piece_index, block_offset, data):
        self.piece_index = piece_index
        self.block_offset = block_offset
        self.block_data = data

    def send_bytes(self):
        # TODO add support for seeding
        raise NotImplementedError("The app doesn't support sending Piece messages")

    @classmethod
    def parse(cls, data):
        size, message_id = struct.unpack(">IB", data[0:5])
        if message_id == cls.message_id:
            piece_index, block_offset = struct.unpack(">II", data[5:13])
            return cls(piece_index, block_offset, data[13:])
        return None


class Cancel(Message):
    # TODO add support for Cancel
    message_id = 8

    def __init__(self):
        raise NotImplementedError("The app doesn't support sending Cancel messages")

    def send_bytes(self):
        raise NotImplementedError("The app doesn't support sending Cancel messages")

    @classmethod
    def parse(cls):
        raise NotImplementedError("The app doesn't support sending Cancel messages")
