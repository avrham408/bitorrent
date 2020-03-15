import pytest
from collections import OrderedDict
from torrent.torrent_file import od_get_key, valid_torrent_path, read_file, decode_raw_data
from os import listdir

TEST_FILES_DIR = 'test_files/' 

#od_get_key
def test_od_get_key_functional():
    od = OrderedDict({'a':'b', (1, 2): 62233, "adar": ['java', 'disc']}) #OrderedDict data
    for key in od.keys():
        assert od_get_key(od, key) == od[key]


def test_od_get_key_error():
    od = OrderedDict({'a':'b', (1, 2): 62233, "adar": ['java', 'disc']}) #OrderedDict data
    #mandat = True
    with pytest.raises(KeyError):
        od_get_key(od, 'c', True)
    with pytest.raises(KeyError):
        od_get_key(od, (1,3), True)
    with pytest.raises(TypeError):
        od_get_key(od, ['a'], True)
    #no mandat
    assert od_get_key(od, ['a']) == None 
    assert od_get_key(od, (1,3)) == None 
    assert od_get_key(od, 'c') == None
    #mandat == False
    assert od_get_key(od, ['a'], False) == None 
    assert od_get_key(od, (1,3), False) == None 
    assert od_get_key(od, 'c', False) == None


def test_od_get_key_bed_types():
    test_dict = {'a':'b', (1, 2): 62233, "adar": ['java', 'disc']}
    #n
    with pytest.raises(TypeError):
        od_get_key(test_dict, 'a', True)
    od = OrderedDict(test_dict) #OrderedDict data
    #not enough variables
    with pytest.raises(TypeError):
        od_get_key(od)


def test_valid_torrent_file_functionl():
    test_files =  listdir(TEST_FILES_DIR)
    for test_torrent_file in test_files:
        if test_torrent_file.endswith('.torrent'):
            assert valid_torrent_path(TEST_FILES_DIR + test_torrent_file) != False
        else:
            assert valid_torrent_path(TEST_FILES_DIR + test_torrent_file) == False 


def test_valid_torrent_file_file_not_exist():
    test_files = ['../file_not_exist', TEST_FILES_DIR + 'file_that_not_exist']
    for test_torrent_file in test_files:
        assert valid_torrent_path(TEST_FILES_DIR + test_torrent_file) == False 


def test_valid_torrent_file_file_bed_input():
    assert valid_torrent_path(['1']) == False
    assert valid_torrent_path(1) == False


def test_read_file_functional():
    test_files =  listdir(TEST_FILES_DIR)
    for test_torrent_file in test_files:
        path = TEST_FILES_DIR + test_torrent_file
        if valid_torrent_path(path):
            assert type(read_file(path)) == bytes
            
def test_decode_raw_data_functional():
    assert decode_raw_data(b'i123e') 

    test_files =  listdir(TEST_FILES_DIR)
    for test_torrent_file in test_files:
        path = TEST_FILES_DIR + test_torrent_file
        if valid_torrent_path(path):
            decode_file = decode_raw_data(read_file(path))
            assert type(decode_file) == OrderedDict

def test_decode_raw_data_not_bencoding_bytes():
    assert decode_raw_data(b'avi') == False
    assert decode_raw_data(TEST_FILES_DIR + 'bad_file') == False #add to good valid torrent file garbage




if __name__ == "__main__":
    test_decode_raw_data_not_bencoding_bytes()
