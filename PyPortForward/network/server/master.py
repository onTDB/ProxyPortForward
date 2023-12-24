import PyPortForward as ppf


from threading import Thread
from json import loads, dumps
import socket

from .client import close_connection
import PyPortForward.network.server as _server

reqid = 0

class ProxyConnection(_server.Connection):
    def __init__(self, sock: socket.socket, proxyid: str):
        super().__init__(sock, proxyid)
    
    def entry(self):
        self.send(f"MODE MASTER".encode())
        dt = str(self.recv(1024))
        if dt != "CHANGEMODE MASTER":
            ppf.logger.error(f"Invalid mode")
            self.close()
            return False
        if dt.split(" ")[1].lower() != "master":
            ppf.logger.error(f"Invalid mode")
            self.close()
            return False
        
        if not self.startencrypt():
            return False
        
        self.send(f"PASS {ppf.config.servers[self.proxyid].passwd}")
        
        pass

def master_entry(sock: socket.socket, proxyid: str) -> bool:
    sock.send(f"MODE MASTER".encode())
    dt = str(sock.recv(1024))
    if not dt.startswith("CHANGEMODE"):
        ppf.logger.error(f"Invalid mode")
        return False
    if dt.split(" ")[1].lower() != "master":
        ppf.logger.error(f"Invalid mode")
        return False
    
    sock.send(f"ENCRYPT START".encode())
    dt = str(sock.recv(1024))
    if dt != "ENCRYPT START":
        ppf.logger.error(f"Invalid encryption")
        return False
    cipher = ppf.network.secure.new_connection_server(sock, dt.split(" ")[1])

    ppf.connections[proxyid] = {
        "master": sock,
        "cipher": cipher,
        "ports": {},
        "portmap": {},
    }

    Thread(target=proxy_master, args=(proxyid,)).start()
    return True

# SERVER <--- PROXY (MASTER)
def proxy_master(proxyid: str):
    """
    Proxy master connection to proxy server.
    """
    sock = ppf.connections[proxyid]["master"]
    cipher = ppf.connections[proxyid]["cipher"]

    while True:
        dt = sock.recv(1024)
        if not dt:
            ppf.logger.error(f"Connection to proxy master closed.")
            break

        dt = loads(cipher.decrypt(dt))

        if dt["type"] == ppf.types.RETURN:
            if dt["status"]: ppf.logger.info(f"[{dt['requid']}] {dt['msg']}")
            else:  ppf.logger.error(f"[{dt['requid']}] {dt['msg']}")
            continue

        elif dt["type"] == ppf.types.NEW_CONNECTION:
            master_ip = sock.getpeername()[0]
            master_port = sock.getpeername()[1]
            info = {
                "portid": dt["portid"],
                "clientid": dt["clientid"],
            }

            # TODO: Maybe start Thread here?
            ppf.network.server.connect_proxy_entry(master_ip, master_port, proxyid, ppf.types.CONNECTION, info)
        
        elif dt["type"] == ppf.types.CLOSE_CONNECTION:
            close_connection(proxyid, dt["portid"], dt["clientid"])
        
        elif dt["type"] == ppf.types.CLOSE_PORT:
            close_port(proxyid, dt["portid"])
            break

        elif dt["type"] == ppf.types.CLOSE_ALL:
            kill_all_connections(proxyid)
            break

def kill_all_connections(proxyid: str):
    for portid in ppf.connections[proxyid]["ports"]:
        close_port(proxyid, portid)
    
    try:
        ppf.connections[proxyid]["master"].close()
    except:
        pass

    del ppf.connections[proxyid]

def close_port(proxyid: str, portid: str):
    for clientid in ppf.connections[proxyid]["ports"][portid]["clients"]:
        close_connection(proxyid, portid, clientid)
    
    del ppf.connections[proxyid]["portmap"][portid]