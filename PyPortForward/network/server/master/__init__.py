import PyPortForward as ppf

from threading import Thread
from json import loads, dumps
import websockets
import asyncio
import socket
import uuid

async def proxy_accept(conn, conn_addr):
    """
    Accept a socket connection
    """
    
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
    if dt != f"PASS {ppf.passwd}":
        ppf.logger.error(f"[{conn_addr}] Unauthenticated connection")
        conn.close()
        return
    conn.send("PASS OK") # EVERY ACCEPT OK

    srvid = uuid.uuid4().hex
    ppf.connections["origin"][srvid] = {
        "master": conn,
        "ports": {},
        "portmap": {},
    }



async def proxy(conn):
    """
    SERVER --> PROXY (MASTER)
    """

    while True:
        data = loads(await conn.recv())
        if data["type"] == ppf.types.NEW_PORT:


def new_port(port: int, srvid: str):
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

    uuid = uuid.uuid4().hex
    ppf.connections["origin"][srvid]["ports"][uuid] = {}
    ppf.connections["origin"][srvid]["portmap"][uuid] = sock
    Thread(target=client_accept, args=(sock, uuid)).start()


def get_port(socket: socket.socket):
    return socket.getsockname()[1]

def open_connection(clientid: str):
    """
    Open connection to proxy server.
    """

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((ppf.host, ppf.port))
    except ConnectionRefusedError:
        ppf.logger.error(f"Unable to connect to proxy server")
        return False

    sock.send("PROXY HELLO")
    dt = str(sock.recv(1024))
    if dt != "CLIENT HELLO":
        ppf.logger.error(f"Invalid HELLO connection")
        sock.close()
        return False

    sock.send(f"VERSION PyPortForward {ppf.__version__}")
    dt = str(sock.recv(1024))
    if not dt.startswith("VERSION"):
        ppf.logger.error(f"Invalid version")
        sock.close()
        return False
    serverver = dt.split(" ")[2]