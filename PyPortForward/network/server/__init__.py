import PyPortForward as ppf


import socket

from .master import master_entry
from .client import client_entry


def connect_proxy_entry(host: str, port: int, proxyid: str, typ: int, info: dict = {}) -> bool:
    """
    Open Master connection to proxy server.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, port))
    except ConnectionRefusedError:
        ppf.logger.error(f"Unable to connect to {host}:{port}")
        return False
    
    sock.send("PROXY HELLO".encode())
    dt = str(sock.recv(1024))
    if dt != "CLIENT HELLO":
        ppf.logger.error(f"Invalid HELLO connection")
        return False
    
    sock.send(f"VERSION PyPortForward {ppf.__version__}".encode())
    dt = str(sock.recv(1024))
    if not dt.startswith("VERSION"):
        ppf.logger.error(f"Invalid version")
        return False
    
    if typ == ppf.types.MASTER:
        return master_entry(sock, proxyid)
    elif typ == ppf.types.CONNECTION:
        return client_entry(sock, proxyid, info)
        
class Connection():
    def __init__(self, sock: socket.socket, proxyid: str):
        self.config = ppf.conf.master[proxyid]
        self.sock = sock
        self.proxyid = proxyid
        self.cipher = None
        self.encrypted = False
        self.send = self.sendplain
        self.recv = self.recvplain
        pass

    def close(self):
        self.sock.close()
        pass

    def startencrypt(self) -> bool:
        self.sock.send(f"ENCRYPT START".encode())
        dt = str(self.sock.recv(1024))
        if dt != "ENCRYPT START":
            ppf.logger.error(f"Invalid encryption")
            self.sock.close()
            return False
        self.cipher = ppf.network.secure.new_connection_server(self.sock, dt.split(" ")[1])
        self.send = self.sendencrypt
        self.recv = self.recvencrypt
        self.encrypted = True
        return True

    def sendplain(self, dt: bytes):
        return self.sock.send(dt)
    
    def sendencrypt(self, dt: bytes):
        return self.sock.send(self.cipher.encrypt(dt))

    def recvplain(self, length):
        return self.sock.recv(length)
    
    def recvencrypt(self, length):
        return self.cipher.decrypt(self.sock.recv(length))