import PyPortForward as ppf

def proxy_accept(sock):
    """
    Accept a socket connection
    """
    try:
        buffer = sock.recv(120)
        info, buffer = ppf.network.parse_info(buffer)
        if info["mode"] == "OPEN":
            if ppf.users.auth(info["client_id"]):
                ppf.logger.info(f"[Accepted] {sock.getsockname()} <- {sock.getpeername()} (User: {info['client_id']})")
                info, buffer = ppf.network.attach_info(info, buffer)
                sock.send(buffer)
                pass
            else:
                ppf.logger.info(f"[Rejected] {sock.getsockname()} <- {sock.getpeername()} (User: {info['client_id']})")
                reject = {"mode": "CLOSE"}
                info, buffer = ppf.network.attach_info(reject, buffer)
                sock.send(buffer)
                return
    except Exception as e:
        ppf.logger.error(f"Error accepting socket: {e}")
        return
