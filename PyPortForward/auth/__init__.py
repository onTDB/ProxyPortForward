import PyPortForward as ppf

def auth(passwd: str):
    if passwd == ppf.passwd:
        return True
    return False