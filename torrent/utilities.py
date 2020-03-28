from queue import Queue
from threading import Thread
from collections import OrderedDict
import logging

logger = logging.getLogger(__name__)

#utilities
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

def od_get_key(od, key, mandat=False):
    """
    the function get OrederdDict object key and mandet
    the function try to get back the data from the od 
    if it mandat raise the error if the key is not mandat 
    return None
    """
    if type(od) != OrderedDict:
        raise TypeError(f'od_get_key get {type(od)} and not OrderdDict object')
    if type(mandat) != bool:
        raise TypeError(f"od_get_key get '{mandat}' for mandat variable the function get only bool type" )
    try:
        return od[key]
    except KeyError as e:
        if mandat:
            logger.warning(f'od_get_key get({type(od)},{type(key)},{mandat}) and raise KeyError', exc_info=True)
            raise e
        else:
            return None
    except TypeError as e:
        if mandat:
            logger.warning(f"od_get_key get({od},{key},{mandat}) key variable from type{type(key)}")
            raise e
        else:
            return None
