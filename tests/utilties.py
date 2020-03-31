import requests
import logging

logger = logging.getLogger(__name__)
TEST_FILES_DIR = 'test_files/' 


def valid_internet(f):
    def web_site_online(url='http://www.google.com/', timeout=5):
        try:
            req = requests.get(url, timeout=timeout)
            # HTTP errors are not raised by default, this statement does that
            req.raise_for_status()
            return True
        except requests.HTTPError as e:
            logger.error("HTTPError")
        except requests.ConnectionError:
            logger.error("ConnectionError")
        return False
    
    def wrap(*args, **kwargs):
        if not web_site_online():
            raise AssertionError("no internet connection")
        return f(*args, **kwargs)
    return wrap


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


def kill_thread(t):
    if t.is_alive():
        t._tstate_lock.release()
        t._stop()
    logging.info("avi")
