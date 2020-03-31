from utilties import valid_internet, _files_list, kill_thread
from torrent.tracker import tracker_manager, udp_request
from torrent.peer_manager import Peer_manager
from torrent.torrent_file import generate_torrent_file
import logging
from time import sleep 
from random import choice


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
                pass

        #close
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
    sleep(10) 
    assert not peer_manager.peers.empty()
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



    

if __name__ == "__main__":
    test_udp_request_http_tracker()



