import socket
import logging

import PyPortForward as ppf

connections = {}

def handle_proxy(buffer, direction, src, client_id, server_name, connection_id):
    '''
    intercept the data flows between local port and the target port
    '''

    src_ip, src_port = src.getsockname()
    if direction:#connections[connection_id]["server"]["name"]
        logging.info(f"{src_ip}:{src_port} ({client_id}) -> {server_name} ({connection_id}) :: {len(buffer)} bytes")
        info, buffer = ppf.network.attach_info(client_id, connection_id, buffer)
    else:
        logging.info(f"{src_ip}:{src_port} ({client_id}) <- {server_name} ({connection_id}) :: {len(buffer)} bytes")
        info, buffer = ppf.network.parse_info(buffer)
    return info, buffer

def handle_server(buffer, direction, client_id, origin, connection_id, proxy_name):
    '''
    intercept the data flows between local port and the target port
    '''
    origin_ip, origin_port = origin.getsockname()
    if direction:
        logging.debug(f"{proxy_name} ({client_id}) -> {origin_ip}:{origin_port} ({connection_id}) :: {len(buffer)} bytes")
        info, buffer = ppf.network.parse_info(buffer)
    else:
        logging.debug(f"{proxy_name} ({client_id}) <- {origin_ip}:{origin_port} ({connection_id}) :: {len(buffer)} bytes")
        info, buffer = ppf.network.attach_info(client_id, connection_id, buffer)
    return info, buffer

def transfer_info(src, dst, client_id, server_name, connection_id, direction):
    '''
    Pass with information to the destination
    '''
    src_ip, src_port = src.getsockname()
    dst_ip, dst_port = dst.getsockname()
    while True:
        try:
            buffer = src.recv(4096)
            if len(buffer) > 0:
                if direction:
                    info, buffer = handle_proxy(buffer, direction, src, client_id, server_name, connection_id)
                else:
                    info, buffer = handle_server(buffer, direction, client_id, src, connection_id, server_name)
                dst.send(buffer)
        except Exception as e:
            logging.error(repr(e))
            break
    logging.warning(f"Closing connect {src_ip}:{src_port}! ")
    src.close()
    ppf.commands.send_command(command="close", connection_id=connection_id, client_id=client_id)

def transfer_raw(src, dst, client_id, server_name, connection_id, direction):
    src_ip, src_port = src.getsockname()
    dst_ip, dst_port = dst.getsockname()
    while True:
        try:
            buffer = src.recv(4096)
            if len(buffer) > 0:
                if direction:
                    info, buffer = handle_server(buffer, direction, client_id, dst, connection_id, server_name)
                else:
                    info, buffer = handle_proxy(buffer, direction, src, client_id, server_name, connection_id)
        except Exception as e:
            logging.error(repr(e))
            break

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
                info, buffer = handle(buffer, True, client_id, connection_id, connections)
                server.send(buffer)
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
                info, buffer = handle(buffer, direction, client_id, connection_id, connections)
                connections[connection_id]["clients"][info["client_id"]].send(buffer)
        except Exception as e:
            logging.error(repr(e))
            break
    logging.warning(f"Closing connection from {connections[connection_id]['server']['name']} ({connection_id})! ")
    server.close()
    del(connections[connection_id])

def to_origin(connection_id, proxy_id, connections):
    proxy = connections["proxy"][proxy_id]
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