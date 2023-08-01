import socket
import websockets
from tempfile import tempdir
from threading import Thread
import uuid

import PyPortForward as ppf

def client(proxy, proxy_port, mode):
    
    uid = uuid.uuid4().hex
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect((server_host, server_port))
    conn.send(ppf.network.attach_info(uid, "", "OPEN", ""))
    s = Thread(target=temp, args=(conn,))
    s.daemon = True
    s.start()
    while True:
        p = ppf.session.prompt("PyPortForward> ")
        if ppf.session.lastcmd == "exit":
            break
        conn.send(ppf.network.attach_info(uid, "", "DATA", p.encode()))
    conn.send(ppf.network.attach_info(uid, "", "CLOSE", ""))
    conn.close()

    pass

def parse(proxy, proxy_port, mode):
    if mode == "sock":
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if ":" in proxy:
                sock.connect((proxy.split(":")[0], int(proxy.split(":")[1])))
            else:
                sock.connect((proxy, proxy_port))
            return sock
        except Exception as e:
            ppf.logger.error(e)
            raise e
    elif mode == "ws":
        try:
            if ":" in proxy:
                sock = websockets.connect(f"ws://{proxy}")
            else:
                sock = websockets.connect(f"ws://{proxy}:{proxy_port}")
            return sock
        except Exception as e:
            ppf.logger.error(e)
            raise e
    elif mode == "wss":
        try:
            if ":" in proxy:
                sock = websockets.connect(f"wss://{proxy}")
            else:
                sock = websockets.connect(f"wss://{proxy}:{proxy_port}")
            return sock
        except Exception as e:
            ppf.logger.error(e)
            raise e
    else:
        ppf.logger.error(f"Unknown mode {mode}")
        raise e