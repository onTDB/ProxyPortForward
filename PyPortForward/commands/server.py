import json
import logging
import socket
from threading import Thread
import websockets
import asyncio

import PyPortForward as ppf

def server(host, port, mode):
    """
    PortForward Manager start point
    """

    if mode == "sock":
        ppf.network.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ppf.network.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        ppf.network.server_socket.bind((host, port))
        ppf.network.server_socket.listen(0x40)
        while True:
            try:
                sock, address = ppf.network.server_socket.accept()
            except KeyboardInterrupt:
                break
            ppf.logger.info(f"[Establishing] {ppf.network.server_socket.getsockname()} <- {host, port} (User: ?)")
            thr = Thread(target=ppf.network.proxy_accept, kwargs={'sock': sock})
            thr.daemon = True
            thr.start()
    elif mode in ["ws", "wss"]:

        pass
    else:
        ppf.logger.error(f"Invalid mode: {mode}")
        return


def server_socket(host, port):
    """
    PortForward Manager start point
    """
    ppf.network.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ppf.network.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    ppf.network.server_socket.bind((host, port))
    ppf.network.server_socket.listen(0x40)
    while True:
        try:
            sock, address = ppf.network.server_socket.accept()
        except KeyboardInterrupt:
            break
        ppf.logger.info(f"[Establishing] {ppf.network.server_socket.getsockname()} <- {host, port} (User: ?)")
        thr = Thread(target=ppf.network.proxy_accept, kwargs={'sock': sock})
        thr.daemon = True
        thr.start()
