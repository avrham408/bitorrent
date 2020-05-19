from torrent.save import create_single_file, save_torrent_file, get_download_path, file_genrator, write_pieces_to_memory
import pytest
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


if __name__ == "__main__":
    test_create_single_file_0_size()
