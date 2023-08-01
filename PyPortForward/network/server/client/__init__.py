import PyPortForward as ppf

import socket
import asyncio

newcon = {}

def proxy_accept_server_socket(sock: socket.socket):
    while True:
        conn, conn_addr = sock.accept()

        dt = str(conn.recv(1024))
        if dt != "PROXY HELLO": 
            ppf.logger.error(f"[{conn_addr}] Invalid HELLO connection")
            conn.close()
            return
        conn.send("CLIENT HELLO")
        
        dt = str(conn.recv(1024))
        if not dt.startswith("VERSION"):
            ppf.logger.error(f"[{conn_addr}] Invalid version")
            conn.close()
            return
        clientver = dt.split(" ")[2]
        # TODO: check version
        conn.send(f"VERSION PyPortForward {ppf.__version__}")

        dt = str(conn.recv(1024))
        if not dt.startswith("PASS"):
            ppf.logger.error(f"[{conn_addr}] Unauthenticated connection")
            conn.close()
            return
        
        clientid = dt.split(" ")[1]
        rtn, info = proxy_accept_server(conn, clientid)
        if rtn == False:
            ppf.logger.error(f"[{conn_addr}] Unauthenticated connection")
            conn.close()
            return
        
        while True:
            data = conn.recv(1024)
            if not data:
                ppf.connections["origin"][info["srvid"]]["ports"][info["port"]][clientid]["client"].close()
                break
            ppf.connections["origin"][info["srvid"]]["ports"][info["port"]][clientid]["client"].send(data)
        del(ppf.connections["origin"][info["srvid"]]["ports"][info["port"]][clientid])
        


async def proxy_accept_server_websocket(conn, path):
    clientid = path.replace("/", "")
    rtn, info = proxy_accept_server(conn, clientid)
    if rtn == False:
        conn.close()
        return
    
    while True:
        data = await conn.recv()
        if not data:
            ppf.connections["origin"][info["srvid"]]["ports"][info["port"]][clientid]["client"].close()
            break
        ppf.connections["origin"][info["srvid"]]["ports"][info["port"]][clientid]["client"].send(data)
    del(ppf.connections["origin"][info["srvid"]]["ports"][info["port"]][clientid])


def proxy_accept_server(conn, clientid):
    if clientid not in newcon:
        return False, None
    coninfo = newcon.pop(clientid)
    ppf.connections["origin"][coninfo["srvid"]]["ports"][coninfo["port"]][clientid]["server"] = conn

    return True, coninfo


def client_accept(sock):
    """
    CLIENT --> PROXY (ACCEPT)
    """
    while True:
        conn, conn_addr = sock.accept()
        









def to_server_socket(srvid: str, portid: str, clientid: str):
    while True:
        data = ppf.connections["origin"][srvid]["ports"][portid][clientid]["client"].recv(1024)
        if not data:
            ppf.connections["origin"][srvid]["ports"][portid][clientid]["server"].close()
            break
        ppf.connections["origin"][srvid]["ports"][portid][clientid]["server"].send(data)
    del(ppf.connections["origin"][srvid]["ports"][portid][clientid])

async def to_server_websocket(srvid: str, portid: str, clientid: str):
    while True:
        data = await ppf.connections["origin"][srvid]["ports"][portid][clientid]["client"].recv()
        if not data:
            ppf.connections["origin"][srvid]["ports"][portid][clientid]["server"].close()
            break
        asyncio.run(ppf.connections["origin"][srvid]["ports"][portid][clientid]["server"].send(data))
    del(ppf.connections["origin"][srvid]["ports"][portid][clientid])


def open_connection(conn: socket.socket, srvid: str):
    """
    Open port on proxy server.
    """
    new = {
        "origin": conn,
        "ports": {},
        "portmap": {},
    }

    ppf.connections["origin"][srvid] = new
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ppf.connections["origin"][srvid]["sock"] = sock
    sock.bind(("