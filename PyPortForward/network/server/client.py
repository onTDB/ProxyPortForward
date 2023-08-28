import PyPortForward as ppf

from threading import Thread
import socket

def client_entry(sock: socket.socket, proxyid: str, info: dict):
    # info = {
    #    "portid": str,
    #    "clientid": str,
    # }

    portid = info["portid"]
    clientid = info["clientid"]

    sock.send("MODE CONNECTION".encode())
    dt = str(sock.recv(1024))
    if dt != "CHANGEMODE CONNECTION":
        ppf.logger.error(f"Invalid mode")
        sock.close()
        return False
    
    sock.send(f"PASS {clientid}")
    dt = str(sock.recv(1024))
    if dt != "PASS OK":
        ppf.logger.error(f"Invalid password or Other ERROR")
        sock.close()
        return False
    
    origin_host = ppf.connections["proxyid"]["portmap"][portid]["host"]
    origin_port = ppf.connections["proxyid"]["portmap"][portid]["port"]

    origin_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        origin_sock.connect((origin_host, origin_port))
    except ConnectionRefusedError:
        ppf.logger.error(f"Unable to connect to {origin_host}:{origin_port}")
        sock.close()
        return False
    
    ppf.connections[proxyid]["ports"][portid][clientid] = {
        "client": sock,
        "server": origin_sock,
    }

    Thread(target=client_to_origin, args=(proxyid, portid, clientid)).start()


def client_to_origin(proxyid: str, portid: str, clientid: str):
    client = ppf.connections[proxyid]["ports"][portid][clientid]["client"]
    server = ppf.connections[proxyid]["ports"][portid][clientid]["server"]

    while True:
        dt = client.recv(1024)
        if not dt:
            close_connection(proxyid, portid, clientid)
            break
        server.send(dt)
    pass

def origin_to_client(proxyid: str, portid: str, clientid: str):
    client = ppf.connections[proxyid]["ports"][portid][clientid]["client"]
    server = ppf.connections[proxyid]["ports"][portid][clientid]["server"]

    while True:
        dt = server.recv(1024)
        if not dt:
            close_connection(proxyid, portid, clientid)
            break
        client.send(dt)
    pass

def client_to_origin_secure(proxyid: str, portid: str, clientid: str):
    client = ppf.connections[proxyid]["ports"][portid][clientid]["client"]
    server = ppf.connections[proxyid]["ports"][portid][clientid]["server"]

    cipher = ppf.connections[proxyid]["ports"][portid][clientid]["cipher"]

    while True:
        dt = client.recv(1024)
        if not dt:
            close_connection(proxyid, portid, clientid)
            break
        server.send(cipher.encrypt(dt))
    pass

def origin_to_client_secure(proxyid: str, portid: str, clientid: str):
    client = ppf.connections[proxyid]["ports"][portid][clientid]["client"]
    server = ppf.connections[proxyid]["ports"][portid][clientid]["server"]

    cipher = ppf.connections[proxyid]["ports"][portid][clientid]["cipher"]

    while True:
        dt = server.recv(1024)
        if not dt:
            close_connection(proxyid, portid, clientid)
            break
        client.send(cipher.decrypt(dt))
    pass

def close_connection(proxyid: str, portid: str, clientid: str):
    try:
        ppf.connections[proxyid]["ports"][portid][clientid]["client"].close()
    except:
        pass
    try:
        ppf.connections[proxyid]["ports"][portid][clientid]["server"].close()
    except:
        pass

    del ppf.connections[proxyid]["ports"][portid][clientid]


