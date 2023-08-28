import PyPortForward as ppf

from .client import client_entry
from .master import master_entry

from threading import Thread
import socket

def proxy_accept(sock: socket.socket):
    """
    Accept a socket connection
    """
    while True:
        conn, conn_addr = sock.accept()
        dt = str(conn.recv(1024))
        if dt != "PROXY HELLO": 
            ppf.logger.error(f"[{conn_addr}] Invalid HELLO connection")
            conn.close()
            continue
        conn.send("CLIENT HELLO")
        
        dt = str(conn.recv(1024))
        if not dt.startswith("VERSION"):
            ppf.logger.error(f"[{conn_addr}] Invalid version")
            conn.close()
            continue
        clientver = dt.split(" ")[2]
        conn.send(f"VERSION PyPortForward {ppf.__version__}")

        dt = str(conn.recv(1024))
        if not dt.startswith("MODE"):
            ppf.logger.error(f"[{conn_addr}] Invalid mode")
            conn.close()
            continue
        
        mode = dt.split(" ")[1]
        if mode.lower() == "master":
            conn.send("CHANGEMODE MASTER")
            Thread(target=master_entry, args=(conn,)).start()
        elif mode.lower() == "connection":
            conn.send("CHANGEMODE CONNECTION")
            Thread(target=client_entry, args=(conn,)).start()
        else:
            ppf.logger.error(f"[{conn_addr}] Invalid mode")
            conn.close()
            continue

