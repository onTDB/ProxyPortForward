import socket
from tempfile import tempdir
from threading import Thread
import uuid

import PyPortForward as ppf

def client(server_host, server_port, login):
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

def temp(sock):
    while True:
        data = sock.recv(4096)
        if len(data) > 0:
            ppf.logger.debug(data)
        else:
            break

def send_command(command, client_id, connection_id):
    pass
