import PyPortForward as ppf

from threading import Thread
import socket
import uuid



newcon = {}
bufferlen = 1024

# SERVER ---> PROXY (OPEN/FIRST)
def client_entry(conn: socket.socket):
    conn_addr = conn.getpeername()
    
    dt = str(conn.recv(1024))
    if not dt.startswith("PASS"):
        ppf.logger.error(f"[{conn_addr}] Unauthenticated connection")
        conn.close()
        return
    
    clientid = dt.split(" ")[1]

    if clientid not in newcon:
        ppf.logger.error(f"[{conn_addr}] Unauthenticated connection")
        conn.send("ERROR UNKNOWN PASS".encode())
        conn.close()
        return
    
    conn.send("PASS OK".encode())

    info = newcon.pop(clientid)
    srvid = info["srvid"]
    portid = info["portid"]

    ppf.connections[srvid]["ports"][portid][clientid]["server"] = conn

# PROXY (OPEN/FIRST)
def open_new_port(srvid: str, port: int, secure: bool):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        sock.bind(("0.0.0.0", port))
        sock.listen(5)
    except OSError:
        ppf.logger.error(f"Unable to open port {port}")
        return False
    

    portid = uuid.uuid4().hex
    ppf.connections[srvid]["ports"][portid] = {}
    ppf.connections[srvid]["portmap"][portid] = {
        "port": port,
        "sock": sock,
        "secure": secure,
    }

    Thread(target=proxy_accept_client, args=(srvid, portid)).start()
    return True, f"Port {port} opened"



# PROXY <--- CLIENT (DATA/FIRST)
def proxy_accept_client(srvid: str, portid: str):
    from .master import send_new_connection

    sock = ppf.connections[srvid]["portmap"][portid]
    while True:
        conn, conn_addr = sock.accept()
        clientid = uuid.uuid4().hex
        
        ppf.connections[srvid]["ports"][portid][clientid] = {
            "client": conn,
            "server": None,
        }
        
        newcon[clientid] = {
            "srvid": srvid,
            "portid": portid,
        }
        
        send_new_connection(srvid, portid, clientid)

        Thread(target=server_to_client, args=(srvid, portid, clientid)).start()
        Thread(target=client_to_server, args=(srvid, portid, clientid)).start()





# SERVER <---> PROXY (DATA)
def server_to_client(srvid: str, portid: str, clientid: str):
    while True:
        if ppf.connections[srvid]["ports"][portid][clientid]["server"] != None and ppf.connections[srvid]["ports"][portid][clientid]["client"] != None:
            break
        
    server = ppf.connections[srvid]["ports"][portid][clientid]["server"]
    client = ppf.connections[srvid]["ports"][portid][clientid]["client"]
    
    while True:
        data = server.recv(bufferlen)
        if not data:
            client.close()
            break
        client.send(data)
    del(ppf.connections[srvid]["ports"][portid][clientid])

def client_to_server(srvid: str, portid: str, clientid: str):
    while True:
        if ppf.connections[srvid]["ports"][portid][clientid]["server"] != None and ppf.connections[srvid]["ports"][portid][clientid]["client"] != None:
            break

    server = ppf.connections[srvid]["ports"][portid][clientid]["server"]
    client = ppf.connections[srvid]["ports"][portid][clientid]["client"]
    
    while True:
        data = client.recv(bufferlen)
        if not data:
            server.close()
            break
        server.send(data)
    del(ppf.connections[srvid]["ports"][portid][clientid])


# SERVER <---> PROXY (DATA/SECURE)
def server_to_client_secure(srvid: str, portid: str, clientid: str):
    while True:
        if ppf.connections[srvid]["ports"][portid][clientid]["server"] != None and ppf.connections[srvid]["ports"][portid][clientid]["client"] != None:
            break
        
    server = ppf.connections[srvid]["ports"][portid][clientid]["server"]
    client = ppf.connections[srvid]["ports"][portid][clientid]["client"]
    cipher = ppf.connections[srvid]["cipher"]
    
    while True:
        dt = server.recv(bufferlen)
        if not dt:
            client.close()
            break
        client.send(cipher.decrypt(dt))
    del(ppf.connections[srvid]["ports"][portid][clientid])

def client_to_server_secure(srvid: str, portid: str, clientid: str):
    while True:
        if ppf.connections[srvid]["ports"][portid][clientid]["server"] != None and ppf.connections[srvid]["ports"][portid][clientid]["client"] != None:
            break

    server = ppf.connections[srvid]["ports"][portid][clientid]["server"]
    client = ppf.connections[srvid]["ports"][portid][clientid]["client"]
    cipher = ppf.connections[srvid]["cipher"]
    
    while True:
        data = client.recv(bufferlen)
        if not data:
            server.close()
            break
        server.send(cipher.encrypt(data))
    del(ppf.connections[srvid]["ports"][portid][clientid])
