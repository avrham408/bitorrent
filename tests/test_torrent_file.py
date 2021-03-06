import pytest
from collections import OrderedDict
from torrent.torrent_file import valid_torrent_path, read_file, decode_raw_data, TorrentFile, generate_torrent_file,\
parse_info, create_tracker, _validate_division_by_20
from os import listdir
import logging
from utilities import _files_list

logger = logging.getLogger()

TEST_FILES_DIR = 'test_files/' 


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

def test_tracker_with_https_schema():
    path = _files_list()[3]
    torrent_file = generate_torrent_file(path)
    for tracker in torrent_file.trackers:
        assert tracker.schema == "https" 
        assert tracker.tracker_type == 'http'

def test_tracker_with_http_schema():
    path = _files_list()[2]
    torrent_file = generate_torrent_file(path)
    for tracker in torrent_file.trackers:
        if tracker.tracker_type == 'http':
            assert tracker.schema == "http" 
            
def test_torrent_file_repr():
    files = _files_list()
    for path in files:
        tracker_file = generate_torrent_file(path)
        assert tracker_file

def test_tracker_repr():
    files = _files_list()
    for path in files:
        torrent_file = generate_torrent_file(path)
        for tracker in torrent_file.trackers:
            assert tracker

def test_validate_division_by_20_not_raising_error_with_good_data():
    with open(TEST_FILES_DIR + 'pieces_in_length', 'rb') as f:
        pieces = f.read()
    assert _validate_division_by_20(pieces)

def test_validate_division_by_20_raising_error_with_bed_data():
    with open(TEST_FILES_DIR + 'pieces_not_in_length', 'rb') as f:
        pieces = f.read()
    with pytest.raises(ValueError):
        _validate_division_by_20(pieces)


if __name__ == "__main__":
    pass
