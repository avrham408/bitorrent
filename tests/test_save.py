from torrent.save import create_single_file, save_torrent_file, get_download_path, file_genrator, write_pieces_to_memory \
    , create_map_for_pieces
import pytest
from torrent.torrent_file import generate_torrent_file  
from torrent.pieces import create_piece_manager
import torrent
from utilities import delete_file, _files_list
import random
import os

DIR_NAME = os.path.dirname(torrent.__path__[0])

def test_create_single_file():
    test_path_name = 'test_name_for_test_save'
    create_single_file(test_path_name, 100)
    file_abs_path = os.path.join(DIR_NAME, 'downloads', test_path_name)
    assert os.path.isfile(file_abs_path)
    delete_file(file_abs_path, True)


def test_create_single_file_size():
    for i in range(100):
        test_path_name = f'test_name_for_size_check{i}'
        test_size = random.randint(1, 10000000) * random.randint(1, 10)
        create_single_file(test_path_name , test_size)
        file_abs_path = os.path.join(DIR_NAME, 'downloads', test_path_name)
        assert os.stat(file_abs_path).st_size == test_size 
        delete_file(file_abs_path, True)


def test_create_single_file_0_size():
    with pytest.raises(OSError):
        test_path_name = 'test_name_for_0_size'
        create_single_file(test_path_name, 0)
    delete_file(os.path.join(DIR_NAME, 'downloads', test_path_name))


def test_save_torrent_file():
    for path in _files_list():
        save_torrent_file(path)
        new_torrent_file_path = os.path.join(DIR_NAME, 'torrent_files', os.path.basename(path))
        assert os.path.exists(new_torrent_file_path)
        delete_file(new_torrent_file_path)


def test_save_torrent_file_data_the_same():
    for path in _files_list():
        save_torrent_file(path)
        new_torrent_file_path = os.path.join(DIR_NAME, 'torrent_files', os.path.basename(path))
        with open(path, 'rb') as f:
            base_torrent_file = f.read()
        with open(new_torrent_file_path, 'rb') as f:
            new_torrent_file = f.read()
        assert new_torrent_file == base_torrent_file
        delete_file(new_torrent_file_path)


def test_pieces_map_total_size():
    # the funtion test create_writing_map_for_pieces get all length of data 
    # that going to write for all piece and check that the total data is equal to torrent_file.length
    for path in _files_list():
        torrent_file = generate_torrent_file(path)
        if not torrent_file.multi_file:
            continue
        piece_manager = create_piece_manager(torrent_file)
        map_dict = create_map_for_pieces(torrent_file.files, piece_manager.pieces)
        assert type(map_dict) is dict
        total_size = 0
        for piece, files in map_dict.items():
            total_for_piece = 0
            for file_data in files:
                total_for_piece += file_data[2]
                total_size += file_data[2]
            assert piece.length == total_for_piece
        assert torrent_file.length == total_size


def test_pieces_map_split_pieces_data():
    # this test is not realy smart or dynamic but it help to know
    # that nothing broked
    path = _files_list()[1]
    torrent_file = generate_torrent_file(path)
    piece_manager = create_piece_manager(torrent_file)
    pieces_map = create_map_for_pieces(torrent_file.files, piece_manager.pieces)
    piece = piece_manager.pieces[0]
    files_for_piece = pieces_map[piece]
    assert len(files_for_piece) == 5
    for data in files_for_piece:
        assert data[1] == 0
    piece = piece_manager.pieces[839]
    files_for_piece = pieces_map[piece]
    assert len(files_for_piece) == 2
    assert files_for_piece[0][1] != 0
    assert files_for_piece[1][1] == 0
