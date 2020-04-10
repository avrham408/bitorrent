from utilities import valid_internet, _files_list, kill_thread
from torrent.tracker import tracker_manager, udp_request, http_request, create_url_for_http_tracker
from torrent.peer import Peer_manager
from torrent.torrent_file import generate_torrent_file
import logging
from time import sleep 
from random import choice
from threading import Thread
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)


@valid_internet
def test_tracker_manager_tracker_alive():
    files = _files_list()
    for torrent_path in files:
        log = logging
        torrent_file = generate_torrent_file(torrent_path)
        peer_manager = Peer_manager()
        tracker_threads = tracker_manager(torrent_file, peer_manager)
        sleep(10)
        for thread in tracker_threads:
            if thread.result_queue.empty():
                assert thread.is_alive()
            else:
                assert not thread.is_alive()
            
        for thread in tracker_threads:
            kill_thread(thread)
        

@valid_internet
def test_udp_request_good_tracker():
    files = _files_list()
    torrent_file = generate_torrent_file(files[2])
    peer_manager = Peer_manager()
    for tracker in torrent_file.trackers:
        if tracker.url == 'exodus.desync.com':
            valid_tracker = tracker

    thread = udp_request(valid_tracker, torrent_file, peer_manager) 
    sleep(15) 
    assert peer_manager.peers.empty() == False
    kill_thread(thread)
    

@valid_internet
def test_udp_request_not_valid_tracker():
    #the test check that udp_request cant get http tracker
    path = _files_list()[3]
    torrent_file = generate_torrent_file(path)   
    tracker = torrent_file.trackers[0]
    peer_manager = Peer_manager()
    thread = udp_request(tracker, torrent_file, peer_manager)
    sleep(0.1)
    assert not thread.is_alive()
    kill_thread(thread)
    


@valid_internet
def test_udp_request_tracker_with_no_response():
    path = _files_list()[2]
    torrent_file = generate_torrent_file(path)   
    for tracker in torrent_file.trackers:
        if tracker.url == "tracker.yify-torrents.com" and tracker.tracker_type == 'udp':
            no_res_tracker = tracker
    peer_manager = Peer_manager()
    thread = udp_request(no_res_tracker, no_res_tracker, peer_manager)
    assert thread.is_alive()
    assert peer_manager.peers.empty()
    sleep(30)
    assert thread.is_alive()
    assert peer_manager.peers.empty()
    kill_thread(thread)

@valid_internet
def test_udp_request_tracker_tracker_from_another_torrent():
    files = _files_list()
    for tracker in generate_torrent_file(files[4]).trackers:
        if tracker.url == 'explodie.org':
            tracker_other_torrent = tracker
    torrent_file = generate_torrent_file(files[0])
    peer_manager = Peer_manager()
    thread = udp_request(tracker_other_torrent, torrent_file, peer_manager)
    sleep(1)
    assert not thread.is_alive()
    

@valid_internet
def test_udp_request_http_tracker():
   path = _files_list()[3]
   torrent_file = generate_torrent_file(path)
   peer_manager = Peer_manager()
   thread = udp_request(torrent_file.trackers[0], torrent_file, peer_manager)
   sleep(0.1)
   assert not thread.is_alive()
   assert thread.result_queue.get().value == 2


@valid_internet
def test_udp_request_recursive_true():
   path = _files_list()[3]
   torrent_file = generate_torrent_file(path)
   peer_manager = Peer_manager()
   thread = udp_request(torrent_file.trackers[0], torrent_file, peer_manager, recursive=True)
   assert type(thread) != Thread


def test_create_url_for_http_tracker():
    path = _files_list()[3]
    torrent_file = generate_torrent_file(path)   
    peer_manager = Peer_manager()
    for tracker in torrent_file.trackers:
        #TODO add asser for query string
        url = create_url_for_http_tracker(torrent_file, tracker, torrent_file.length)
        schema, netloc, path, _, query, _ = urlparse(url)
        base_url = schema + '://' +  netloc + path
        assert base_url == 'https://ipv6.torrent.ubuntu.com:443/announce' or base_url == 'https://torrent.ubuntu.com:443/announce'
        

@valid_internet
def test_http_request_good_tracker():
    #TODO the test fail if you run the untest more then one time in a row fix it...
    path = _files_list()[3]
    torrent_file = generate_torrent_file(path)   
    peer_manager = Peer_manager()
    for tracker in torrent_file.trackers:
       if tracker.url == 'torrent.ubuntu.com':
            good_tracker = tracker

    url = create_url_for_http_tracker(torrent_file, tracker,torrent_file.length)
    thread = http_request(url, peer_manager)
    sleep(15)
    assert thread.is_alive()
    assert peer_manager.peers.empty() == False
    kill_thread(thread) 




if __name__ == "__main__":
    test_udp_request_good_tracker()


