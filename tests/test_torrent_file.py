import pytest
from collections import OrderedDict
from torrent.torrent_file import valid_torrent_path, read_file, decode_raw_data, TorrentFile, generate_torrent_file,\
parse_info, create_tracker
from torrent.utilities import od_get_key
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

def _files_list():
    """
    file.torrent - multi file annonunce, announce-list
    file1.torrent - multi file with announce-list and url-list 
    file2.torrent - multi file announce, announce-list
    file3.torrent - single file announce, announce-list
    file4.torrent - multi file  announce, announce-list and url-list 
    file5.torrent - single url-list contain alot of bulshit for future
    """
    
    files = ['file.torrent', 'file1.torrent', 'file2.torrent', 'file3.torrent', 'file4.torrent']
    return [TEST_FILES_DIR + path for path in files]

def test_generate_torrent_file_multi():
    files = _files_list()
    for path in files:
        torrent_file = generate_torrent_file(path)
        od_struct = torrent_file.od_data
        try:
            if od_struct[b'info'][b'files']:
                assert torrent_file.multi_file
        except KeyError:
            assert torrent_file.multi_file == False

def test_generate_torrent_file_path():
    files = _files_list()
    for path in files:
        torrent_file = generate_torrent_file(path)
        assert torrent_file.path == path

def test_generate_torrent_file_trackers():
    files = _files_list()
    for path in files:
        torrent = generate_torrent_file(path)
        list_of_trackers = decode_raw_data(read_file(path))[b'announce-list']
        list_of_trackers = [create_tracker(tracker.decode('utf-8')) for track_list in list_of_trackers for tracker in track_list]
        list_of_trackers = [tracker for tracker in list_of_trackers if tracker]
        for tracker in list_of_trackers:
            assert tracker in torrent.trackers
        

def test_generate_torrent_not_duplicate_tracker():
    files = _files_list()
    for path in files:
        tracker_list = generate_torrent_file(path).trackers
        for _ in range(len(tracker_list)):
            tracker = tracker_list.pop()
            for t in tracker_list:
                assert  t.tracker_type != tracker.tracker_type or t.url != tracker.url or t.path != tracker.path or t.port != tracker.port

            


if __name__ == "__main__":
    pass
