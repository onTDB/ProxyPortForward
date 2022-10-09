import PyPortForward as ppf
import time
import json

"""
UUID: 32 bytes

{"client_id": "00000000000000000000000000000000", "conn_id": "00000000000000000000000000000000", "mode": "CLOSE"}
mode: OPEN, CLOSE, DATA

"""

dtlen = 120

def attach_info(client_id, connection_id, buffer):
    '''
    get the destination information of a connection
    '''
    info = {"client_id": client_id, "conn_id": connection_id}
    buffer = json.dumps(info).encode() + b'\x00' * (dtlen - len(json.dumps(info))) + buffer
    return info, buffer

def parse_info(buffer):
    '''
    parse the destination information of a connection
    '''
    info = buffer[:dtlen].decode().strip('\x00')
    return json.loads(info), buffer[dtlen:]