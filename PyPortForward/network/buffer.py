import PyPortForward as ppf
import time
import json

"""
UUID: 32 bytes

mode: OPEN, CLOSE, DATA
□□□□□{"client_id": "00000000000000000000000000000000", "conn_id": "00000000000000000000000000000000"}

mode: OPT
□□□□□{}


"""
dtlen = 100

def attach_info(client_id: str, connection_id: str, mode: str, buffer: bytes) -> bytes:
    '''
    get the destination information of a connection
    '''
    info = {"client_id": client_id, "conn_id": connection_id}
    info = mode.encode() + b'\x00' * (5 - len(mode)) + json.dumps(info).encode() + b'\x00' * (dtlen - len(json.dumps(info)))
    if len(info) > dtlen+5:
        ppf.logger.error("The length of the information is too long! {clientid}".format(clientid=client_id))
        return None
    
    buffer = info + buffer

    return buffer

 
def parse_info(buffer) -> (str, dict, bytes):
    '''
    parse the destination information of a connection
    '''
    mode = buffer[:5].decode().strip('\x00')
    info = buffer[5:dtlen+5].decode().strip('\x00')

    return mode, json.loads(info), buffer[dtlen+5:]
