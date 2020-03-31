import logging
#from torrent.torrent_file import generate_torrent_file
#from torrent.peer_manager import Peer_manager
from torrent.utilities import run_async, od_get_key
from torrent.bencoding import Decoder
from urllib.parse import urlencode
import requests
from random import randint, randrange
from time import sleep
import struct 
import socket
from enum import Enum

logger = logging.getLogger(__name__)

class UdpError(Enum):
    unknown_error = 0
    info_hash = 1
    not_valid_tracker = 2
    request_error = 3


#udp tracker
@run_async
def udp_request(tracker, torrent_file, peer_manager, wait = 0, recursive=False):
    """ 
    the function get tracker, torrent_file and peer_manager.
    the function 
    wait :

    steps:
        1. connection requeset
        2. announcing:
        3. interval announce
         
        the tracker actions responses:
            0 - connect
            1 - announce
            2 - scrape
            3 - error
    """
    if tracker.tracker_type != "udp":
        logger.error(f"udp_request start with not valid tracker: {tracker}")
        return UdpError.not_valid_tracker
    if wait > 1800:
        wait = 1800
    sleep(wait)
    #request
    logger.debug(f"try to connect {tracker}")
    udp_tracker_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    logger.debug("connect to socket succssed")
    socket_connecion_request = socket_send_to(udp_tracker_socket, tracker,create_connect_req_struct())
    if not socket_connecion_request:
        udp_tracker_socket.close()
        udp_request(tracker, torrent_file, peer_manager, (wait + 60) * 2, recursive=True)
    if socket_connecion_request == UdpError.request_error:
        udp_tracker_socket.close()
        return UdpError.request_error
    connection_res = udp_request_connection_response(udp_tracker_socket)
    if connection_res == 0:
        udp_tracker_socket.close()
        udp_request(tracker, torrent_file, peer_manager, (wait + 60) * 2, recursive=True)
    if connection_res == 1:
        return None
    if type(connection_res) == UdpError:
        return connection_res 
    transcation_id, connection_id = connection_res
    #announce
    while True:
        socket_announce_request = socket_send_to(udp_tracker_socket, tracker,announcing_req_packet(torrent_file, connection_id))
        if socket_announce_request == UdpError.request_error:
            udp_tracker_socket.close()
            return UdpError.request_error
        elif not socket_announce_request:
            udp_tracker_socket.close()
            udp_request(tracker, torrent_file, peer_manager, (wait + 60) * 2, recursive=True)
        announce_response = udp_request_announce_response(udp_tracker_socket)
        if announce_response == 0:
            udp_tracker_socket.close()
            udp_request(tracker, torrent_file, peer_manager, (wait + 60) * 2, recursive=True)
        if announce_response == 1:
            udp_tracker_socket.close()
            return None
        if type(announce_response) == UdpError:
            return announce_response 
        interval, peers = announce_response 
        peer_manager.add_peers(peers)
        logger.info(f"peers add to peer_manager and go to sleep for {interval} seconds")
        sleep(interval)


def udp_request_connection_response(sock):
    """
    errors:
        0 = restart
        1 = kill thread 
        UdpError
    """
    logger.debug("start connection response")
    packet_data = read_response_from_socket(sock)
    if not packet_data:
        logger.debug("connect to tracker failed")
        return 0
    action = packet_data[0]
    if action == 3 :
        return _handle_error_action(packet_data[1][0])
    elif action != 0:
        logger.info(f"somthing got worng with response code for connection the action is {action}")
        return 0
    try:
        return packet_data[1]
    except ValueError as e:
        logger.error("read_response_from_socket return data not in the format", exc_info=True)
        return 1


def socket_send_to(sock, tracker, message):
    try:
        return sock.sendto(message, (tracker.url, tracker.port))
    except socket.gaierror:
        logger.debug("error in open socket")
        return False 
    except Exception:
        logger.error("error in send udp announce request", exc_info=True)
        return UdpError.request_error
       

def udp_request_announce_response(sock):
    """
    errors:
        0 = restart
        1 = kill thread 
        UdpError
    """
    packet_data = read_response_from_socket(sock)
    if not packet_data:
        logger.debug("announce request failed no answer")
        return 0 
    action = packet_data[0]
    if action == 3 :
        return _handle_error_action(packet_data[1][0])

    elif action != 1:
        logger.debug(f"somthing got worng with response code for connection the action is {action}")
        return 1
    try:
        transcation_id, interval, leechers, seeders, peers = packet_data[1]
    except ValueError as e:
        logger.error("read_response_from_socket return data not in the format", exc_info=True)
        return 1 
    return interval, peers

def _handle_error_action(error):
    if error == UdpError.info_hash:
        logger.info("server back with error string of info hash not exist")
        return error
    else:
        return UdpError.unknown_error


def read_response_from_socket(sock):
    """ the function manage reading from socket
        the function get socket that wait from response
        and try recv from socket
        actions:
            all packet of data start with action 
            the function parse the action and parse the data

        the return 'action' and list of relevant data for action
        if it failed the function return None
    """
    #TODO add decorator support from timeout
    logger.debug("start get action code")
    res, _ = sock.recvfrom(4096)
    action = struct.unpack(">I", res[:4])[0]
    if action == 0:
        logger.debug("connet code got from server")
        parsed_res = parse_connect_packet(res[4:]) 
        if not parsed_res:
            logger.info("parse udp connection response failed")
            return None
        transcation_id, connection_id = parsed_res 
        return action, [transcation_id, connection_id]

    elif action == 1:
        logger.debug("announce code got from server")
        parsed_res = parse_announce_packet(res[4:20]) 
        if not parsed_res:
            logger.debug("parse udp announce response failed")
            return None
        transcation_id, interval, leechers, seeders = parsed_res 
        peers = get_peers(res[20:])
        return action, [transcation_id, interval, leechers, seeders, peers]

    elif action == 3:
        #TODO support error from _files[4] error from explodie.org:6969 - "uknown option type"
        error_string = res[8:].decode('utf-8')
        logger.debug(f"error string from server")
        return action, [parse_error_to_code(error_string)]

    else:
        logger.warning(f"response code from server '{code}'")
        return None 
        
    
def parse_connect_packet(packet):
    if len(packet) != 12:
        logger.info(f"packet length for connection response not match got : {packet}")
        return None
    try:
        req_response = struct.unpack(">LQ", packet)
    except struct.debug: 
        logger.info("parse response failed", exc_info=True)
        return None 
    return req_response


def parse_announce_packet(packet):
    if len(packet) != 16:
        logger.info(f"packet length for announce response not match got : {packet}")
        return None
    try:
        return struct.unpack(">IIII", packet)
    except struct.error:
        logger.info(f"parse_announce_res got from udp tracker bed response {res}")
        return None


def create_connect_req_struct(protocol_id=0X41727101980, transcation_id=randrange(0, 65535), action=0):
    #the struct for udp tracker request
    #protocol_id is const, transcation id  is random num , action 0 = connect
    try:
        req_struct = struct.pack(">QLL", protocol_id, action, transcation_id)
    except struct.error:
        raise Excpetion("the udp req struct creation failed")
    return req_struct


def announcing_req_packet(torrent_file, connection_id, left=0, downloaded=0, uploaded=0, event=0):
    action = 1
    transcation_id = randrange(0, 65535)
    peer_id = ('-PC0001-' + ''.join([str(randint(0, 9)) for _ in range(12)])).encode('utf-8')
    ip = 0
    key = 0
    num_want = -1
    port = 9999
    try:
        return struct.pack(">QLL20s20sQQQLLLlI", connection_id, action, transcation_id, torrent_file.info_hash, peer_id, downloaded, left, uploaded, event, ip, key, num_want, port)
    except struct.error:
        logger.info("creating packet failed", exc_info=True)
        return None
    
     
def get_peers(peers):
    peer_list = []
    for peer_pointer in range(0, len(peers), 6):
        try:
            peer = struct.unpack(">IH", peers[peer_pointer: peer_pointer + 6])
        except struct.error:
            logger.info("somthing get worng with unpack peers data")
            return peer_list 
        peer_list.append(peer)
    return peer_list 
    
def parse_error_to_code(error):
    """
    1 unknown option type - info hash is not available
    """
    if "unknown option type" in error.lower().strip():
        return UdpError.info_hash
    else:
        logger.error(f"unknown error - {error}")
        UdpError.unknown_error

#http functions
@run_async
def http_request(url, peer_manager,wait=0, recursive=False):
    if wait > 1800:
        wait = 1800
    sleep(wait) 
    while True:
        logger.debug(f"start http tracker request")
        res = None
        try: 
            res = requests.get(url)
        except requests.exceptions.ConnectionError:
            logger.debug("connect to tracker failed")
            return http_request(url, peer_manager, wait + 30 * 2, recursive=True)
        if res.status_code != 200:
            logger.info(f"requst return with '{res.status_code}' status code")
            http_request(url, peer_manager, wait + 30 * 2, recursive=True)
        parsed_res = read_http_tracker_response(res.content)
        if not parsed_res:
            return http_request(url, peer_manager, wait + 30 * 2)
        interval, peers = parsed_res
        peer_manager.add_peers(peers)
        logger.info(f"peers add to peer_manager and go to sleep for {interval} seconds")
        sleep(interval)


def read_http_tracker_response(content):
    #TODO add support for more exceptions for Decoder
    #TODO check if we need complete and incomplete
    try:
        od = Decoder(content).decode()
    except Exception:
        logger.error("decode http tracker request failed", exc_info=True)
        return None 
    if od_get_key(od, b'failure reason'):
        logger.info("http tracker response with failure reasone")
        logger.info(od[b'failure reason'])
        return None

    #complete = od_get_key(od, b'complete')
    #incomplete = od_get_key(od, b'incomplete')
    interval = od_get_key(od, b'interval', mandat=True)
    peers = get_peers_data(od_get_key(od, b'peers', mandat=True))
    return interval, peers
    
def get_peers_data(peers_in_bytes):
    peers = []
    for bytes_pos in range(0, len(peers_in_bytes), 6):
        peer = peers_in_bytes[bytes_pos: bytes_pos + 6]
        peer_ip = get_ip(peer[:4])
        try:
            peer_port = struct.unpack(">H", peer[4:])[0]
        except struct.error:
            logger.debug("unpacking peers failed")
        peers.append((peer_ip, peer_port))
    return peers


def create_url_for_http_tracker(torrent_file, tracker, left, uploaded=0, downloaded=0, ):
    #TODO fix to consst (that peer id is alwayz the same peer_id
    #check that 'left', 'uploaded', 'downloaded' is real data
    
    params = {
    'info_hash': torrent_file.info_hash,
    'peer_id': '-PC0001-' + ''.join([str(randint(0, 9)) for _ in range(12)]),
    'port': 6889,
    'uploaded': uploaded,
    'downloaded': downloaded,
    'left': left,
    'compact': 1,
    'event' : 'started'#for now hardcode
    }
    return tracker.http_url() + '?' + urlencode(params)

def get_ip(ip_address):
    return '.'.join([str(num) for num in ip_address])


#request manager
def tracker_manager(torrent_file, peer_manager):
    tracker_threads = []
    for tracker in torrent_file.trackers:
        if tracker.tracker_type == 'http':
            url = create_url_for_http_tracker(torrent_file, tracker, torrent_file.length)
            tracker_threads.append(http_request(url, peer_manager))
        elif tracker.tracker_type == 'udp':
            tracker_threads.append(udp_request(tracker, torrent_file, peer_manager))
        else:
            #TODO add support to dht protocol
            pass

    return tracker_threads
        



if __name__ == "__main__":
    pass
