import socket
import logging

import PyPortForward as ppf

connections = {}

def handle(buffer, direction, client_id, connection_id, connections):
    '''
    intercept the data flows between local port and the target port
    '''

    client_ip, client_port = connections[connection_id]["clients"][client_id].getsockname()
    if direction:#connections[connection_id]["server"]["name"]
        logging.debug(f"{client_ip}:{client_port} ({client_id}) -> {connections[connection_id]['server']['name']} ({connection_id}) :: {len(buffer)} bytes")
    else:
        logging.debug(f"{client_ip}:{client_port} ({client_id}) <- {connections[connection_id]['server']['name']} ({connection_id}) :: {len(buffer)} bytes")
    return info, buffer

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
    client = connections[connection_id]["clients"][client_id]
    client_ip, client_port = client.getsockname()
    while True:
        try:
            buffer = client.recv(4096)
            if len(buffer) > 0:
                server.send(handle(buffer, True, client_id, connection_id, connections))
        except Exception as e:
            logging.error(repr(e))
            break
    logging.warning(f"Closing connection from {client_ip, client_port} ({client_id})! ")
    client.close()
    del(connections[connection_id]["clients"][client_id])

def to_client(connection_id, connections):
    server = connections[connection_id]["server"]["socket"]
    while True:
        try:
            buffer = server.recv(4096)
            if len(buffer) > 0:
                handle(buffer, direction, client_id, connection_id, connections)
        except Exception as e:
            logging.error(repr(e))
            break
    logging.warning(f"Closing connection from {connections[connection_id]['server']['name']} ({connection_id})! ")
    server.close()
    del(connections[connection_id])

