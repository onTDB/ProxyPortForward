import socket
from threading import Thread

import PyPortForward as ppf

def server(host, port):
    """
    PortForward Manager start point
    """

    ppf.network.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ppf.network.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    ppf.network.socket.bind((host, port))
    ppf.network.socket.listen(0x40)
    while True:
        try:
            sock, address = ppf.network.socket.accept()
        except KeyboardInterrupt:
            break
        ppf.logger.info(f"[Establishing] {ppf.network.socket.getsockname()} <- {host, port} (User: ?)")
        thr = Thread(target=ppf.network.proxy_accept, kwargs={'sock': sock})
        thr.daemon = True
        thr.start()

