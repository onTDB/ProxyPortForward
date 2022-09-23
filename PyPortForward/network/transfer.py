import socket
import logging

import PyPortForward as ppf

connections = {}

def handle(buffer, direction, client_address, client_port, server_name):
    '''
    intercept the data flows between local port and the target port
    '''
    if direction:
        logging.debug(f"{client_address, client_port} -> {server_name} {len(buffer)} bytes")
    else:
        logging.debug(f"{client_address, client_port} <- {server_name} {len(buffer)} bytes")
    return buffer

def transfer(connection_id, src, direction, connections):
    dst = connections[connection_id]["server"]["socket"]
    src_address, src_port = src.getsockname()
    dst_address, dst_port = dst.getsockname()
    while True:
        try:
            buffer = src.recv(4096)
            if len(buffer) > 0:
                if direction:
                    dst.send(handle(buffer, direction, src_address, src_port, dst_address, dst_port))
                else:
                    src.send(handle(buffer, direction, src_address, src_port, dst_address, dst_port))
                dst.send(handle(buffer, direction, src_address, src_port, dst_address, dst_port))
        except Exception as e:
            logging.error(repr(e))
            break
    logging.warning(f"Closing connect {src_address, src_port}! ")
    src.close()

def to_server(client_id, connection_id, connections):
    server = connections[connection_id]["server"]["socket"]
    client = connections[connection_id]["clients"][client_id]["socket"]
    client_ip, client_port = client.getsockname()
    server_name = connections[connection_id]["server"]["name"]
    while True:
        try:
            buffer = client.recv(4096)
            if len(buffer) > 0:
                server.send(handle(buffer, True, client_ip, client_port, server_name))
        except Exception as e:
            logging.error(repr(e))
            break

