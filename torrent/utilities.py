from queue import Queue
from torrent.io import get_path
from threading import Thread
from collections import OrderedDict
import logging

logger = logging.getLogger(__name__)


def run_async(f, daemon=False):
    def wrapped_f(q, *args, **kwargs):
        ret = f(*args, **kwargs)
        q.put(ret)

    def wrap(*args, **kwargs):
        try:
            if kwargs.get('recursive'):
                return f(*args, **kwargs)
        except KeyError:
            pass
        q = Queue()
        t = Thread(target=wrapped_f, args=(q, ) + args, kwargs=kwargs)
        t.daemon = daemon
        t.start()
        t.result_queue = q
        return t
    return wrap


def get_download_path(file_name):
    return get_path('downloads', file_name)


def get_torrent_files_path(file_name):
    return get_path('torrent_files', file_name)


def handle_exception(func, error_message, error_type=Exception, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except error_type:
        logger.debug(error_message)
        return False


def close_thread(thread):
    if thread.is_alive():
        thread._tstate_lock.release()
        thread._stop()
