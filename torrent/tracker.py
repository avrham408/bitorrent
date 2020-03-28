import logging
#from torrent.torrent_file import generate_torrent_file
from torrent.utilities import run_async, od_get_key
from torrent.bencoding import Decoder
from urllib.parse import urlencode
import requests
from random import randint, randrange
from time import sleep
import struct 
import socket

logger = logging.getLogger(__name__)

#udp tracket
@run_async
def udp_request(tracker, torrent_file, peer_manager, wait = 0):
    """ 
    the function get tracker object and request for peers
    steps:
        1. connection requeset
        2. announcing:
        3. interval announce
         
        the tracker responses:
            0 - connect
            1 - announce
            2 - scrape
            3 - error
    """
    if wait > 1800:
        wait = 1800
    sleep(wait)
    #connection request
    logger.debug(f"try to connect {tracker}")
    udp_tracker_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    connect_message = create_connect_req_struct()    
    logger.debug("connect to socket")
    try:
        socket_connecion_request  = udp_tracker_socket.sendto(connect_message, (tracker.url, tracker.port))
    except socket.gaierror:
        logger.debug("error in open socket")
        udp_request(tracker, torrent_file, peer_manager, (wait + 1) * 2)
    except Exception:
        logger.error("error in open sockt", exc_info=True)
        return False

    #connection rsponse 
    logging.debug("start connection response")
    packet_data = read_response_from_socket(udp_tracker_socket)
    if not packet_data:
        logging.debug("connect to peer failed")
        udp_tracker_socket.close()
        udp_request(tracker, torrent_file, peer_manager, (wait + 1) * 4)

    action = packet_data[0]
    if action == 3 :
        #TODO handle 3 action
        logging.info(f"server response with error- {packet_data[1]}")
        udp_tracker_socket.close()
        return None 
    elif action != 0:
        logging.info(f"somthing got worng with response code for connection the action is {action}")
        udp_tracker_socket.close()
        udp_request(tracker, torrent_file, peer_manager, (wait + 1) * 4)
    try:
        transcation_id, connection_id = packet_data[1]
    except ValueError as e:
        logging.error("read_response_from_socket return data not in the format", exc_info=True)
        return None

    #announce request
    while True:
        announce_message = announcing_req_packet(torrent_file, connection_id)
        try:
            socket_connecion_request  = udp_tracker_socket.sendto(announce_message, (tracker.url, tracker.port))
        except Exception:
            logger.info("error in send udp announce request", exc_info=True)
            udp_tracker_socket.close()
            udp_request(tracker, torrent_file, peer_manager, (wait + 1) * 4)

        #announce response
        packet_data = read_response_from_socket(udp_tracker_socket)
        if not packet_data:
            logging.debug("announce request failed no answer")
            udp_tracker_socket.close()
            udp_request(tracker, torrent_file, peer_manager, (wait + 60) * 2)
        action = packet_data[0]
        if action == 3 :
            #TODO handle 3 action
            logging.info(f"server response with error- {packet_data[1]}")
            udp_tracker_socket.close()
            return None 
        elif action != 1:
            logging.debug(f"somthing got worng with response code for connection the action is {action}")
            udp_tracker_socket.close()
            return None 
        try:
            transcation_id, interval, leechers, seeders, peers = packet_data[1]
        except ValueError as e:
            logging.error("read_response_from_socket return data not in the format", exc_info=True)
            return None
        peer_manager.add_peers(peers)
        sleep(interval)
    

def read_response_from_socket(sock):
    #TODO add decorator support from timeout
    logging.debug("start get action code")
    res, _ = sock.recvfrom(4096)
    action = struct.unpack(">I", res[:4])[0]
    if action == 0:
        logging.debug("connet code got from server")
        parsed_res = parse_connect_packet(res[4:]) 
        if not parsed_res:
            logger.info("parse udp connection response failed")
            return None
        transcation_id, connection_id = parsed_res 
        return action, [transcation_id, connection_id]

    elif action == 1:
        logging.debug("announce code got from server")
        parsed_res = parse_announce_packet(res[4:20]) 
        if not parsed_res:
            logger.debug("parse udp announce response failed")
            return None
        transcation_id, interval, leechers, seeders = parsed_res 
        peers = get_peers(res[20:])
        return action, [transcation_id, interval, leechers, seeders, peers]

    elif action == 3:
        logging.info("error code got from server")
        error_string = res[4:].decode['utf-8']
        logger.debug(f"error string from server - {error_string}")
        return action, [error_string]

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
        logging.info("creating packet failed", exc_info=True)
        return None
    
     
def get_peers(peers):
    peer_list = []
    for peer_pointer in range(0, len(peers), 6):
        try:
            peer = struct.unpack(">IH", peers[peer_pointer: peer_pointer + 6])
        except struct.error:
            logging.info("somthing get worng with unpack peers data")
            return peer_list 
        peer_list.append(peer)
    return peer_list 
    

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
        logging.debug("add peers to peer_manager successed")
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
        logging.info("http tracker response with failure reasone")
        logging.info(od[b'failure reason'])
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
            logging.debug("unpacking peers failed")
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
def request_manager(torrent_file):
    pass

if __name__ == "__main__":
    pass
