from torrent.peer_protocol import Handshake, Choke, Unchoke, Interested, Have, BitField, Request, Piece
from torrent.torrent_file import generate_torrent_file
from torrent.pieces import create_piece_manager 
from utilities import  _files_list 
from struct import pack
import pytest
from bitarray import bitarray


def test_create_handshake():
    files = _files_list()
    for f in files: 
        torrent_file = generate_torrent_file(f)
        info_hash = torrent_file.info_hash
        peer_id = torrent_file.peer_id
        handshake = Handshake(info_hash, peer_id)
        protocol = 'BitTorrent protocol'.encode('utf-8')
        valid_packet = pack('>B19s8x20s20s', 19, protocol, info_hash, peer_id.encode('utf-8'))
        assert handshake.send_bytes() == valid_packet


def test_parse_handshake():
    files = _files_list() 
    for f in files: 
        torrent_file = generate_torrent_file(f)
        info_hash = torrent_file.info_hash
        peer_id = torrent_file.peer_id
        handshake = Handshake(info_hash, peer_id)
        protocol = 'BitTorrent protocol'.encode('utf-8')
        valid_packet = pack('>B19s8x20s20s', 19, protocol, info_hash, peer_id.encode('utf-8'))
        new_handshake = Handshake.parse(handshake.send_bytes())
        assert new_handshake.send_bytes() == handshake.send_bytes()
        assert Handshake.parse(b'\x13BitTorrent protocol\x00\x00\x00\x00\x00\x00\x00\x00\xdd\x82U\xec\xdc|\xa5_\xb0\xbb\xf8\x13#\xd8pb\xdb\x1fm\x1c-PC0001-713259777527')


def test_parse_choke():
    choke_message = Choke.parse(b'\x00\x00\x00\x01\x01')
    assert choke_message


def test_choke_send_bytes():
    choke = Choke()
    assert choke.send_bytes() == b'\x00\x00\x00\x01\x01'


def test_parse_choke_not_choke_message():
    message = b'\x00\x00\x00\x01\x00'
    assert Choke.parse(message) == None


def test_parse_unchoke():
    unchoke_message = Unchoke.parse(b'\x00\x00\x00\x01\x00')
    assert unchoke_message


def test_unchoke_send_bytes():
    unchoke = Unchoke()
    assert unchoke.send_bytes() == b'\x00\x00\x00\x01\x00'


def test_parse_unchoke_not_unchoke_message():
    message = b'\x00\x00\x00\x01\x01'
    assert Unchoke.parse(message) == None


def test_parse_interested():
    interested_message = Interested.parse(b'\x00\x00\x00\x01\x02')
    assert interested_message


def test_interested_send_bytes():
    interested_message  = Interested()
    assert interested_message.send_bytes() == b'\x00\x00\x00\x01\x02'


def test_parse_interested_not_interested_message():
    message = b'\x00\x00\x00\x01\x01'
    assert Interested.parse(message) == None


def test_have_send_bytes_not_implemented():
    have_message = Have(1)
    with pytest.raises(NotImplementedError):
        have_message.send_bytes()


def test_have_parse():
    message = b'\x00\x00\x00\x04\x04\x00\x00\x00\x01'
    have_message = Have.parse(message)
    assert have_message.piece_index == 1


def test_bitfiled_creation():
    bitfield_example = b"\x00\x00\x0d\x05\xff\xbf\xfd\xff\xff\xff\xff\xf7\xff\xff\xff\xff\xbf\xff\xff\xff\xff\xfd\xff\xff\xff\xff\xff\xef\xfe\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xfd\xff\xef\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xf7\xff\xff\xff\xff\xff\xff\xff\xdf\xdf\xff\xae\xff\xff\xef\xff\x7f\xff\xff\xff\xff\xf7\xff\xff\x7f\xff\xfb\xff\xff\xff\xff\xff\xff\xff\xff\xff\xf7\xff\xff\xff\xfe\xff\xff\xff\xf7\xff\xff\xbf\xff\xff\xff\xff\xff\xff\xff\xff\xfb\xff\xff\xff\xff\xff\xff\xff\xff\xf7\xff\xfd\xff\xff\xff\xfb\xff\xfb\xff\xff\xff\xff\xff\xff\xff\xdf\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xfd\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xfb\xff\xef\xff\xf7\xff\xfb\xff\xff\xff\xff\xff\xff\xff\xff\xfe\xff\xff\xff\xff\xff\xff\xff\xff\xbf\xff\xff\xff\xfd\xff\xff\xff\xff\xff\xff\xff\xff\xfb\xff\xff\xff\xff\xff\xff\xff\xff\xf7\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xf7\xff\xff\xff\xff\xff\xff\xff\xef\xff\xff\xff\xff\xff\xff\xfb\xff\xff\xff\xf7\xff\xff\xff\xff\xff\xff\xfd\xff\xff\xff\xff\xff\xff\xf7\xdf\xff\xff\xfd\xff\xff\xff\xff\xff\xef\xff\xff\xff\xef\xff\xff\xfc"
    bitfield_message = BitField(bitfield_example) 
    assert bitfield_message
    assert bitfield_message.available_positions


def test_bitfield_parse_bitfield():
    bitfield_example = b'\x00\x00\x00\t\x05\xbf\xfd\xff\xff\xff'
    bitarray_bitfields = BitField._parse_bitfield(bitfield_example[5:])
    bitarray_to_compare = bitarray()
    bitarray_to_compare.frombytes(bitfield_example[5:])
    assert bitarray_to_compare == bitarray_bitfields


def test_bitfield_send_bytes_not_implmented():
    test_data = b'\x00\x00\x00\t\x05\xbf\xfd\xff\xff\xff'
    bitfield_message = BitField.parse(test_data) 
    with pytest.raises(NotImplementedError):
        bitfield_message.send_bytes()
    

def test_bitfield_not_bitfield_message():
    bed_bitfield = b'\x00\x00\x00\t\x01\xbf\xfd\xff\xff\xff'
    assert not BitField.parse(bed_bitfield) 

@pytest.mark.asyncio
async def test_request_creation():
    torrent_file = generate_torrent_file(_files_list()[3])
    piece_manager = create_piece_manager(torrent_file)
    block_size = 2 ** 14
    for i in range(100):
        piece = await piece_manager.get_piece()
        piece_size = torrent_file.piece_length
        block_offset = 0
        for i in range(int(piece_size / block_size)):
            request_message = Request(piece.index, block_offset, block_size)
            block_offset += block_size
            assert request_message

def test_request_parse_request_exception():
    with pytest.raises(NotImplementedError):
        Request.parse()


def test_request_send_bytes():
    request_message = Request(0,0, 2 ** 14)
    assert request_message.send_bytes() == pack('>IBIII', 13, 6, 0, 0, 2 ** 14)


def test_create_piece():
    #i created a file with bytes that contain the data of piece 0 block 0 in file3.torrent
    with open('test_files/piece_message.bytes', 'rb') as f:
        piece_data = f.read() 

    piece = Piece.parse(piece_data)
    assert piece
    assert len(piece.block_data) == 2 ** 14
    assert piece.piece_index == 0
    assert piece.block_offset == 0


def test_piece_send_bytes_not_implmented():
    piece = Piece(0,0, b'\x00\x00')
    assert piece
    with pytest.raises(NotImplementedError):
        piece.send_bytes()
