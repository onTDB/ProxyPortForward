from threading import Thread
import socket
import logging

import PyPortForward as ppf

connections = {}

"""
PROXY
{
    "origin": {
        "UUID": { # Connection_id
            "server": "UUID", # Server_id
            "clients": {
                "UUID1": socket.socket(),
                "UUID2": socket.socket()
            },
        }
    },
    "server": {
        "UUID": { # Server_id
            "name": "onTDB's Server 01",
            "socket": socket.socket(),
        }
    }
}

SERVER
{
    "origin": {
        "UUID": {
            "ip": "0.0.0.0",
            "port": 1234,
            "clients": {
                "UUID1": socket.socket(),
                "UUID2": socket.socket()
            },
            #"clientthreads": {
            #    "UUID1": Thread(),
            #    "UUID2": Thread()
            #}
        }
    },
    "proxy": socket.socket()
}
"""

def handle_proxy(buffer, direction, src, client_id, server_name, connection_id): #direction: true ==> goto origin server
    '''
    intercept the data flows between local port and the target port
    '''
    src_ip, src_port = src.getsockname()
    if direction:#connections[connection_id]["server"]["name"]
        info, buffer = ppf.network.attach_info(client_id, connection_id, buffer)
        logging.info(f"{src_ip}:{src_port} ({client_id}) -> {server_name} ({connection_id}) :: {len(buffer)} bytes")
    else:
        info, buffer = ppf.network.parse_info(buffer)
        connection_id = info["conn_id"]
        client_id = info["client_id"]
        src_ip, src_port = connections["origin"][connection_id]["clients"][client_id].getsockname()
        logging.info(f"{src_ip}:{src_port} ({client_id}) <- {server_name} ({connection_id}) :: {len(buffer)} bytes")
    return info, buffer

def handle_server(buffer, direction, client_id, origin, connection_id, proxy_name):
    '''
    intercept the data flows between local port and the target port
    '''
    origin_ip, origin_port = origin.getsockname()
    if direction:
        info, buffer = ppf.network.parse_info(buffer)
        connection_id = info["conn_id"]
        client_id = info["client_id"]
        origin_ip, origin_port = connections["origin"][connection_id]["socket"].getsockname()
        logging.debug(f"{proxy_name} ({client_id}) -> {origin_ip}:{origin_port} ({connection_id}) :: {len(buffer)} bytes")
    else:
        info, buffer = ppf.network.attach_info(client_id, connection_id, buffer)
        logging.debug(f"{proxy_name} ({client_id}) <- {origin_ip}:{origin_port} ({connection_id}) :: {len(buffer)} bytes")        
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
                if direction: # Proxy -> Server
                    info, buffer = handle_proxy(buffer, direction, src, client_id, server_name, connection_id)
                else: # Server -> Proxy
                    info, buffer = handle_server(buffer, direction, client_id, src, connection_id, server_name)
                dst.send(buffer)
        except Exception as e:
            logging.error(repr(e))
            if direction and dst.fileno() == -1:
                logging.critical(msg="Origin socket is closed!")
                break
            elif not direction and src.fileno() == -1:
                logging.critical(msg="Proxy socket is closed!")
                break
            break
    if direction:
        for sock in connections["origin"][connection_id]["clients"].values():
            sock.close()
    else:
        for sock in connections["origin"].values():
            sock.close()

def transfer_client(origin, server_name):
    origin_ip, origin_port = origin.getsockname()
    while True:
        try:
            buffer = origin.recv(4096)
            if len(buffer) > 0:
                info, buffer = handle_proxy(buffer, False, src, None, server_name, None)
                if info["mode"] == "CLOSE":
                    logging.warning(f"Closing connect {origin_ip}:{origin_port}! (Server Request)")
                    connections["origin"][info["conn_id"]][info["client_id"]].close()
                    del(connections["origin"][info["conn_id"]]["clients"][info["client_id"]])
                connections["origin"][info["conn_id"]]["server"]["socket"].send(buffer)
        except Exception as e:
            logging.error(repr(e))
            # Check socket are closed
            if origin.fileno() == -1:
                logging.critical(msg="Origin socket is closed!")
                break
            break

def transfer_origin(proxy, proxy_name):
    proxy_ip, proxy_port = proxy.getsockname()
    while True:
        try:
            buffer = proxy.recv(4096)
            if len(buffer) > 0:
                info, buffer = handle_server(buffer, True, None, proxy, None, proxy_name)
                if info["mode"] == "OPEN":
                    newconn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    newconn.connect((connections["origin"][info["conn_id"]]["ip"], connections["origin"][info["conn_id"]]["port"]))
                    connections["origin"][info["conn_id"]]["clients"][info["client_id"]] = newconn
                    logging.info(f"New connection {info['client_id']} to {connections['origin'][info['conn_id']]['ip']}:{connections['origin'][info['conn_id']]['port']} ({info['conn_id']})")
                    
                    newthr = threading.Thread(target=transfer_info, args=(newconn, proxy, info["client_id"], proxy_name, info["conn_id"], False))
                    newthr.daeomon = True
                    newthr.start()
                    #connections["origin"][info["conn_id"]]["clientthreads"][info["client_id"]] = newthr
                    continue
                elif info["mode"] == "CLOSE":
                    logging.warning(f"Closing connect {proxy_ip}:{proxy_port}! (Client Request)")
                    connections["origin"][info["conn_id"]]["clients"][info["client_id"]].close()
                    del(connections["origin"][info["conn_id"]]["clients"][info["client_id"]])
                    #del(connections["origin"][info["conn_id"]]["clientthreads"][info["client_id"]])
                    continue
                connections["origin"][info["conn_id"]]["clients"][info["client_id"]].send(buffer)
        except Exception as e:
            logging.error(repr(e))
            # Check socket are closed
            if proxy.fileno() == -1:
                logging.critical(msg="Proxy socket is closed!")
                break
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
