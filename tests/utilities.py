import requests
import logging
import os

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


def delete_file(src, assert_exception=False):
    if assert_exception:
        try:
            os.remove(src)
        except FileNotFoundError:
            assert False #file not found for deletion
    else:
        try:
            os.remove(src)
        except FileNotFoundError:
            pass

def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print('%r  %2.2f ms' % \
                  (method.__name__, (te - ts) * 1000))
        return result
    return timed
