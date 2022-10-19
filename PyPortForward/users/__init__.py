import PyPortForward as ppf

def auth(client_id):
    """
    Authenticate a client
    """
    ppf.logger.debug(f"Authenticating client {client_id}")
    return True
