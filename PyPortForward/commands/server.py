from flask import Flask, request
from flask_cors import CORS
import json
from threading import Thread
import logging
import socket

import PyPortForward as ppf

app_thread = None
sock_thread = None
app = Flask(__name__)
CORS(app)
logging.getLogger('werkzeug').handlers = [ppf.PromptHandler()]

@app.route('/', methods=['GET'])
def index():
    return "PyPortForward Server\nHello World!"


def server(host, port, port_sock):
    """
    PortForward Manager start point
    """
    logging.getLogger('werkzeug').setLevel(logging.getLogger('PyPortForward').getEffectiveLevel())
    app_thread = Thread(target=app.run, kwargs={'host': host, 'port': port, 'debug': ppf.logger.getEffectiveLevel() == logging.DEBUG})
    app_thread.daemon = True
    app_thread.start()

    sock_thread = Thread(target=server_socket, args=(host, port))
    sock_thread.daemon = True
    sock_thread.start()
    logging.info("Server started")
    while True:
        try:
            sock_thread.join()
            app_thread.join()
        except KeyboardInterrupt:
            break

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
