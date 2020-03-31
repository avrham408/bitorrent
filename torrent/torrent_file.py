from torrent.bencoding import Encoder, Decoder
from torrent.utilities import od_get_key
import logging
from enum import Enum
from hashlib import sha1
from os.path import isfile
from urllib.parse import urlsplit
from random import randint
 
logger = logging.getLogger(__name__)

#classes

class TorrentFile():
    def __init__(self, struct_dict):
        self.multi_file = struct_dict['multi_file']
        self.path = struct_dict['path']
        self.od_data = struct_dict['orderd_content'] # all the data in OrderdDict object
        self.trackers = struct_dict['trackers']
        self.info_hash = struct_dict['info_hash']
        if self.multi_file:
            self.files = struct_dict['files']
        self.length = struct_dict['length']
        self.piece_length = struct_dict['piece_length']
        self.name = struct_dict['name']
        if type(self.name) == bytes:
            self.name = self.name.decode('utf-8')
        self.pieces = struct_dict['pieces']
        self.raw_content = struct_dict['raw']
        self.id = '-PC0001-' + ''.join([str(randint(0, 9)) for _ in range(12)])

    def __repr__(self):
        return f"torrent_file({self.name})"


class Tracker():
    #TODO think if this is the right place hold this object and if the the future the tracker going to
    #manage the connection
    """
    the object contain 2 types of trackers udp or http trackers
    url(domain):str, path:str, type:'http' or 'udp, port:'int'
    """
    def __init__(self, tracker_type, url, path,  port=80):
        self.schema = tracker_type
        self.url = url
        self.path = path
        self.port = port

        if tracker_type == 'https':
            self.tracker_type = 'http'
        else:
            self.tracker_type = tracker_type 

    def http_url(self):
        return f'{self.schema}://{self.url}:{self.port}{self.path}'

    def __repr__(self):
        return f'tracker({self.schema}:{self.url}:{self.port}{self.path})'

    def __hash__(self):
        return hash(self.url)

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and self.url == other.url and self.tracker_type == other.tracker_type and self.port == other.port)

    def __ne__(self, other):
        return not self.__eq__(self, other)
    



#help functions

#torrent parse functions
def valid_torrent_path(path):
    # the function valid torrent object path
    if type(path) != str:
        logger.error(f"the path type is {type(path)} the function vaild_torrent_path get only string")
        return False
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


def decode_raw_data(raw_data):
    """
        the function get bits object and return 
        the file decode in bencoding format
    """
    try: 
        return Decoder(raw_data).decode()
    except (RuntimeError, TypeError) as e:
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
    info_data['files'], info_data['length'] = parse_files_data(od_get_key(info_od, b'files', True))
    if not info_data['files']:
        logger.error("parsing torrent file failed")
        return False
    return info_data 

def parse_files_data(file_list):
    #only relevant for multi files because they have 'files' header
    parsed_list = []
    total_length = 0
    for od_file in file_list: #OrderdDict file
        file_data = {}
        file_data['length'] = od_get_key(od_file, b'length', True)
        total_length += file_data['length']
        # the path list consist one or more subdirectorys and the last file is the name of the file
        file_data['path'] = od_get_key(od_file, b'path', True)
        parsed_list.append(file_data)
    return parsed_list, total_length


def single_file_parse(info_od):
    info_data = {'multi_file': False}
    info_data['length'] = od_get_key(info_od, b'length', True)
    info_data['name'] = od_get_key(info_od, b'name', True)
    info_data['piece_length'] = od_get_key(info_od, b'piece length', True)
    info_data['pieces'] = od_get_key(info_od, b'pieces', True)
    return info_data 


def create_tracker(url):
    protocol, netloc , path, _, _ = urlsplit(url)
    protocol 
    if protocol == 'wss': #temp for deletion in future
    #TODO support wss protocol
        return None
    if protocol != 'udp' and protocol != 'http' and protocol !=  'https':
        logger.warning(f'the trackers {url} not conatin protocol')
        return None
    if netloc.find(':') == -1:
        url = netloc
        if protocol == 'http':
            port = 80
        else:
            port = 443
    else:
        url, port = netloc.split(':')
        port = int(port)
    return Tracker(protocol, url, path, port)


def get_trackers(od_torrent):
    announce_list = od_get_key(od_torrent, b'announce-list')
    url_list =  od_get_key(od_torrent, b'url-list')
    single_announce =  od_get_key(od_torrent, b'announce')
    trackers = []
    
    if announce_list:
        trackers += [create_tracker(url.decode('utf-8'))  for list_of_url in announce_list for url in list_of_url]
    if single_announce: 
        trackers += [create_tracker((single_announce).decode('utf-8'))]
    if url_list: #TODO add support to wss tracker type (b'url-list' header) 
        pass
    return list(set(trackers))
    


def get_torrent_data(path):
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
    file_content = decode_raw_data(file_content)
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
    torrent_cont['trackers'] = [tracker for tracker in trackers if tracker]
    if not torrent_cont['trackers']:
        logger.warning("the torrent file not contain any valid trackers")
        return False
    #path 
    torrent_cont['path'] = path
    return torrent_cont
     

def generate_torrent_file(path):
    torrent_data_dict = get_torrent_data(path)
    if not torrent_data_dict:
        logger.warning('create  TorrentFile object failed')
        return False
    return TorrentFile(torrent_data_dict)

