import PyPortForward as ppf

from threading import Thread
from json import loads, dumps
import socket
import uuid

def master_entry(conn: socket.socket): # Thread entry
    """
    Accept a socket connection as master
    """
    conn_addr = conn.getpeername()

    dt = str(conn.recv(1024))
    if dt != "ENCRYPT START":
        ppf.logger.error(f"[{conn_addr}] Unencrypted connection is not available")
        conn.close()
        return
    conn.send("ENCRYPT START")

    cipher = ppf.network.secure.new_connection_proxy(conn, dt.split(" ")[1])

    dt = str(cipher.decrypt(conn.recv(1024)))
    if not dt.startswith("PASS"): 
        ppf.logger.error(f"[{conn_addr}] Invalid process")
        conn.close()
        return
    passwd = dt.split(" ")[1]
    
    result = ppf.auth.auth(passwd)
    if not result:
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

def proxy_master(srvid: str) -> None:
    from .client import open_new_port
    
    if srvid not in ppf.connections: return
    conn = ppf.connections[srvid]["master"]
    cipher = ppf.connections[srvid]["cipher"]

    while True:
        dt = conn.recv(1024)
        if not dt: 
            kill_all_connections(srvid)
            break

        dt = loads(cipher.decrypt(dt))
        if dt["type"] == ppf.types.RETURN:
            if dt["status"]: ppf.logger.info(f"[{srvid}] {dt['msg']}")
            else:  ppf.logger.error(f"[{srvid}] {dt['msg']}")
            continue
        if dt["type"] == ppf.types.NEW_PORT:
            status, msg = open_new_port(srvid, dt["port"], dt["secure"])
        elif dt["type"] == ppf.types.CLOSE_CONNECTION:
            status, msg = close_connection(srvid, dt["portid"], dt["clientid"])
        elif dt["type"] == ppf.types.CLOSE_PORT:
            status, msg = close_port(srvid, dt["portid"])
        elif dt["type"] == ppf.types.CLOSE_ALL:
            kill_all_connections(srvid)
            break
        else:
            status, msg = False, "Invalid type"
        
        send = {
            "type": ppf.types.RETURN,
            "reqid": dt["reqid"],
            "status": status,
            "msg": msg,
        }

        conn.send(cipher.encrypt(dumps(send).encode()))

def send_new_connection(srvid: str, portid: str, clientid: str) -> None:
    """
    New connection from client
    """

    send = {
        "type": ppf.types.NEW_CONNECTION,
        "portid": portid,
        "clientid": clientid,
    }

    ppf.connections[srvid]["master"].send(dumps(send).encode())


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

def kill_all_connections(srvid: str):
    try:
        ppf.connections[srvid]["master"].send(ppf.connections[srvid]["cipher"].encrypt(dumps({"type": ppf.types.CLOSE_ALL})))
    except:
        pass
    
    for portid in ppf.connections[srvid]["ports"]:
        close_port(srvid, portid)

    try:
        ppf.connections[srvid]["master"].close()
    except:
        pass

    del ppf.connections[srvid]
