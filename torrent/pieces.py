from enum import Enum
from hashlib import sha1
import logging

logger = logging.getLogger(__name__)

class PieceStatus(Enum):
    free = 0 
    in_progress = 1
    done = 2

class Piece():
    """The piece object reprsent one piece from pieces in the info of torrent file
    all piece in size of piece length fro torrent file hoz me except from the last piece
    the piece come with info hash of 20 bytes in sha1 and if the piece data the came
    from peer in sha1 not the same like the piece hash the piece is not right"""
    def __init__(self, piece_hash, length, piece_index):
        self.index = piece_index
        self.piece_hash = piece_hash
        self.length = length
        self.blocks = []
        self.status = PieceStatus.free

    def valid_sha1(self):
        validation = sha1(self.piece_hash).digest() ==  sha1(b''.join(self.blocks)).digest()
        if validation:
            logger.debug(f'piece {self.index} is valid')
            self.status = PieceStatus.done
        else:
            logger.debug(f'piece {self.index} is not valid')
            self._lost_piece()
        return validation 

    def _lost_piece(self):
        self.debug(f"we lost a piece in index {self.index}")
        self.status = PieceStatus.free
        self.block = []

    def add_block(self, block):
        logger.debug(f"block add to piece {self.index}")
        self.blocks.append(block)
    
    def __repr__(self):
        return f"{self.index}:{self.status.name}"

class Piece_Manager():
    """
        the class porpuse is to manage the connection from piece to the place in
        the memory on file. for now it only a list with data
    """
    def __init__(self):
        self.pieces = []
        self.piece_amount = 0

    def add_piece(self, piece):
        if type(piece) != Piece:
            raise Exception(f"add piece to Piece manager failed the object appended in not piece is {self.piece}")
        self.pieces.append(piece)
        return True

    def pieces_status(self):
        in_progress = 0
        free = 0
        done = 0
        for piece in self.pieces:
            if piece.status == PieceStatus.free:
                free += 1
            elif piece.status == PieceStatus.in_progress:
                in_progress += 1
            elif piece.status == PieceStatus.done:
                done += 1
            else:
                raise Exception(f"{piece.index} have not valid status - {piece.status}")
                logger.error(exc_info=True)
        return {Pieces_status.free: free, PieceStatus.done: done, PieceStatus.in_progress: in_progress}


def create_piece_manager(torrent_file):
    piece_manager = Piece_Manager()
    piece_length = torrent_file.piece_length
    index = 1
    for piece_pointer in range(0, len(torrent_file.pieces) - 20, 20):
        piece_manager.add_piece(Piece(torrent_file.pieces[piece_pointer:piece_pointer+20], piece_length, index))
        index += 1
    last_piece = Piece(torrent_file.pieces[20* index - 20: 20 * index], torrent_file.length % piece_length, index)
    piece_manager.add_piece(last_piece)
    return piece_manager
