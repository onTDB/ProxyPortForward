import PyPortForward as ppf
import time
import json

def attach_info(client_id, connection_id, buffer):
    '''
    get the destination information of a connection
    '''
    info = {"client_id": client_id, "conn_id": connection_id}
    buffer = json.dumps(info).encode() + b'\x00' * (100 - len(json.dumps(info))) + buffer
    return info, buffer

def parse_info(buffer):
    '''
    parse the destination information of a connection
    '''
    info = buffer[:100].decode().strip('\x00')
    return json.loads(info), buffer[100:]