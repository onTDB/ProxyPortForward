import PyPortForward as ppf

from threading import Thread
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


def client_accept(sock, uuid):
    """
    CLIENT --> PROXY (ACCEPT)
    """
    while True:
        conn, conn_addr = sock.accept()
        
    pass



def open_proxy_port(conn, port: int):
    """
    Open port on proxy server.
    """
    new = {
        "port": port,
        "origin": conn,
        "clients": {},
    }

    uuid = uuid.uuid4().hex
    ppf.connections["origin"][uuid] = new
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind(("0.0.0.0", port))
    except OSError:
        ppf.logger.error(f"Port {port} already in use")
        return False
    sock.listen(0x40)
    ppf.logger.info(f"Opened port {port} ({uuid})")

    Thread(target=client_accept, kwargs={'sock': sock, 'uuid': uuid}).start()

    


