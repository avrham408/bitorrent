from torrent.bencoding import Encoder, Decoder
import logging
from enum import Enum
from hashlib import sha1
from os.path import isfile
from collections import OrderedDict
from urllib.parse import urlsplit

logger = logging.getLogger(__name__)

#classes

class TorrentFile(object):
    def __init__(self, struct_dict):
        self.path = struct_dict['path']
        self.trackers = struct_dict['trackers']
        self.info_hash = struct_dict['info_hash']
        self.files = struct_dict['files']
        self.length = struct_dict['length']
        self.piece_length = struct_dict['piece_length']
        self.name = struct_dict['name']
        self.pieces = struct_dict['pieces']
        self.raw_content = struct_dict['raw']

class Tracker(object):
    #TODO think if this is the right place hold this object and if the the future the tracker going to
    #manage the connection
    """
    the object contain 2 types of trackers udp or http trackers
    url(domain):str, path:str, type:'http' or 'udp, port:'int'
    """
    
    def __init__(self, url,port, path, tracker_type):
       self.url = url
       self.path = path
       self.tracker_type = tracker_type



#help functions
def od_get_key(od, key, mandat=False):
    """
    the function get OrederdDict object key and mandet
    the function try to get back the data from the od 
    if it mandat raise the error if the key is not mandat 
    return None
    """
    if type(od) != OrderedDict:
        raise TypeError(f'od_get_key get {type(od)} and not OrderdDict object')
    try:
        return od[key]
    except KeyError as e:
        if mandat:
            raise e
        else:
            return None
        

#torrent parse functions
def valid_torrent_path(path):
    # the function valid torrent object path
    if not isfile(path):
        logger.error(f"the path {path} is not a File")
        return False
    if not path.endswith(".torrent"):
        logger.error(f"the file {path} suffix is not .torrent")
        return False 
    return True
    

def read_file(path):
    try:
        with open(path, 'rb') as f:
            return f.read()
    except FileNotFoundError:
        logger.error("read file problem", exc_info=True)
        return False


def decode_file(raw_data):
    """
        the function get bits object and return 
        the file decode in bencoding format
    """
    try: 
        return Decoder(raw_data).decode()
    except RuntimeError as e:
        logger.error("file content not in bencoding format", exc_info=True)
        return False


def get_info_hash(file_content):
    #The SHA1 hash of the info dict found in the .torrent
    #from https://markuseliasson.se/article/bittorrent-in-python/
    try:
        info = od_get_key(file_content, b'info', True)
    except KeyError:
        logget.error("torrent file 'info' header is not exist")
        return False
    return sha1(Encoder(info).encode()).digest()


def parse_info(info_od):
    #the function seprate multi file and single file torrent objects
    if od_get_key(info_od, b'files', False):
        return multi_file_parse(info_od)
    else:
        return single_file_parse(info_od)


def multi_file_parse(info_od):
    info_data = {'multi_file': True}
    info_data['name'] = od_get_key(info_od, b'name', True)
    info_data['piece_length'] = od_get_key(info_od, b'piece length', True)
    info_data['pieces'] = od_get_key(info_od, b'pieces', True)
    info_data['files'] = parse_files_data(od_get_key(info_od, b'files', True))
    if not info_data['files']:
        logger.error("parsing torrent file failed")
        return False
    return info_data 

def parse_files_data(file_list):
    #only relevant for multi files because they have 'files' header
    parsed_list = []
    for od_file in file_list: #OrderdDict file
        file_data = {}
        file_data['length'] = od_get_key(od_file, b'length', True)
        # the path list consist one or more subdirectorys and the last file is the name of the file
        file_data['path'] = od_get_key(od_file, b'path', True)
        parsed_list.append(file_data)
    return parsed_list


def single_file_parse(info_od):
    info_data = {'multi_file': False}
    info_data['length'] = od_get_key(info_od, b'length', True)
    info_data['name'] = od_get_key(info_od, b'name', True)
    info_data['piece_length'] = od_get_key(info_od, b'piece length', True)
    info_data['pieces'] = od_get_key(info_od, b'pieces', True)
    return info_data 

def create_tracker(bytes_url):
    pass

def get_trackers(od_torrent):
    announce_list = od_get_key(od_torrent, b'announce-list')
    if not announce_list:
        return [create_tracker(od_get_key[b'announce'])]
    else:
        pass
        
        



def parse_content(path):
    """
       main function in torrent file
       the function get file path and return dict with all torrent file data or false
       res
    """
    #valid type
    if not valid_torrent_path(path):
        return False
    torrent_cont = {}     

    #read file
    file_content = read_file(path)
    if not file_content:
        return False
    torrent_cont['raw'] = file_content

    #decode file
    file_content = decode_file(file_content)
    torrent_cont['orderd_content'] = file_content
    if not torrent_cont['orderd_content']:
        return False

    #get info hash
    torrent_cont['info_hash'] = get_info_hash(file_content) 
    if not torrent_cont['info_hash']:
        return False
    
    #parse_info
    info_parsed = parse_info(od_get_key(file_content, b'info', True))
    if not info_parsed:
        return false
    torrent_cont.update(info_parsed)

    #trackers
    trackers =  get_trackers(file_content)



    return torrent_cont
