import PyPortForward as ppf

from Cryptodome.Cipher import AES
from threading import Thread
from json import loads, dumps
import socket
import uuid

from .client import client_accept

def master_entry(conn: socket.socket): # Thread entry
    """
    Accept a socket connection as master
    """
    conn_addr = conn.getpeername()

    dt = str(conn.recv(1024))
    if not dt.startswith("ENCRYPT"):
        ppf.logger.error(f"[{conn_addr}] Unencrypted connection is not available")
        conn.close()
        return
    
    cipher: AES = ppf.network.secure.new_connection_proxy(conn, dt.split(" ")[1])

    dt = str(cipher.decrypt(conn.recv(1024)))
    if not dt.startswith("PASS"): 
        ppf.logger.error(f"[{conn_addr}] Invalid HELLO connection")
        conn.close()
        return
    passwd = dt.split(" ")[1]
    if passwd != ppf.passwd:
        ppf.logger.error(f"[{conn_addr}] Invalid password")
        conn.close()
        return

    conn.send(cipher.encrypt("PASS OK"))

    srvid = uuid.uuid4().hex
    ppf.connections[srvid] = {
        "master": conn,
        "cipher": cipher,
        "ports": {},
        "portmap": {},
    }

    proxy_master(srvid)
    return

def proxy_master(srvid: str):
    if srvid not in ppf.connections: return
    conn = ppf.connections[srvid]["master"]
    cipher = ppf.connections[srvid]["cipher"]

    while True:
        dt = cipher.decrypt(conn.recv(1024))
        if not dt: 
            kill_all_connections(srvid)
            break

        dt = loads(dt)
        if dt["type"] == ppf.types.NEW_PORT:
            open_new_port(srvid, dt["port"], dt["secure"])
        elif dt["type"] == ppf.types.CLOSE_CONNECTION:
            close_connection(srvid, dt["portid"], dt["clientid"])
        elif dt["type"] == ppf.types.CLOSE_PORT:
            close_port(srvid, dt["portid"])
        elif dt["type"] == ppf.types.CLOSE_ALL:
            kill_all_connections(srvid)
            break

def open_new_port(srvid: str, port: int, secure: bool = False):
    """
    Open port on proxy server.
    """

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind(("0.0.0.0", port))
        sock.listen(5)
    except OSError:
        ppf.logger.error(f"Unable to open port {port}")
        return False

    portid = uuid.uuid4().hex
    ppf.connections[srvid]["ports"][portid] = {}
    ppf.connections[srvid]["portmap"][portid] = {
        "port": port,
        "sock": sock,
        "secure": False,
    }
    Thread(target=client_accept, args=(sock, srvid, portid)).start()

def send_new_connection(srvid: str, portid: str, clientid: str):
    """
    New connection from client
    """

    send = {
        "type": ppf.types.NEW_CONNECTION,
        "portid": portid,
        "clientid": clientid,
    }

    ppf.connections[srvid]["master"].send(dumps(send).encode())

    return clientid

def send_close_connection(srvid: str, portid: str, clientid: str) -> str:
    """
    Close connection from client
    """

    send = {
        "type": ppf.types.CLOSE_CONNECTION,
        "portid": portid,
        "clientid": clientid,
    }

    ppf.connections[srvid]["master"].send(dumps(send).encode())

    return clientid

def close_connection(srvid: str, portid: str, clientid: str) -> None:
    """
    Close connection from server
    """

    try:
        ppf.connections[srvid]["ports"][portid][clientid]["client"].close()
    except:
        pass
    try:
        ppf.connections[srvid]["ports"][portid][clientid]["server"].close()
    except:
        pass

    del ppf.connections[srvid]["ports"][portid][clientid]
    return

def close_port(srvid: str, portid: str) -> None:
    """
    Close port on proxy server.
    """
    for clientid in ppf.connections[srvid]["ports"][portid]:
        close_connection(srvid, portid, clientid)
    
    try:
        ppf.connections[srvid]["portmap"][portid].close()
    except:
        pass
    
    del ppf.connections[srvid]["portmap"][portid]
    return

def kill_all_connections(srvid: str):
    for portid in ppf.connections[srvid]["ports"]:
        for clientid in ppf.connections[srvid]["ports"][portid]:
            try:
                ppf.connections[srvid]["ports"][portid][clientid]["client"].close()
            except:
                pass
            try:
                ppf.connections[srvid]["ports"][portid][clientid]["server"].close()
            except:
                pass
    for portid in ppf.connections[srvid]["portmap"]:
        try:
            ppf.connections[srvid]["portmap"][portid].close()
        except:
            pass
    try:
        ppf.connections[srvid]["master"].close()
    except:
        pass
    del ppf.connections[srvid]
