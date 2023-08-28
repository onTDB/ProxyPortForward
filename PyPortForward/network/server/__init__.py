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
        
