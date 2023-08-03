import PyPortForward as ppf

from Cryptodome.Cipher import AES
from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import PKCS1_OAEP
from Cryptodome.Random import get_random_bytes
from base64 import b64encode, b64decode
from pathlib import Path
from json import dumps, loads
import socket

def _new_cipher(srvid: str) -> (str, str, AES):
    '''
    generate a new cipher
    '''
    key = get_random_bytes(32)
    iv = get_random_bytes(16)
    key_b64 = b64encode(key).decode()
    iv_b64 = b64encode(iv).decode()
    
    cipher = AES.new(key, AES.MODE_CFB, iv)
    ppf.logger.info(f"New cipher generated for {srvid}")
    
    return key, iv, cipher

def _load_cipher(srvid: str, key: str, iv: str) -> AES:
    '''
    load a cipher
    '''
    key = b64decode(key)
    iv = b64decode(iv)
    return AES.new(key, AES.MODE_CFB, iv)

def new_connection_proxy(conn: socket.socket) -> AES:
    dt = loads(conn.recv(1024).decode())
    if dt["type"] != ppf.types.PUBKEY:
        conn.close()
        return
    
    pubkey = RSA.import_key(dt["pubkey"])
    cipher = PKCS1_OAEP.new(pubkey)
    key, iv, cipher = _new_cipher()
    dt = {
        "type": ppf.types.AES,
        "key": key,
        "iv": iv,
    }
    dt = cipher.encrypt(dumps(dt).encode())
    conn.send(dt)
    return cipher

def new_connection_server(conn: socket.socket) -> AES:
    privkey = RSA.generate(2048)
    cipher = PKCS1_OAEP.new(privkey)
    pubkey = privkey.publickey()

    dt = {
        "type": ppf.types.PUBKEY,
        "pubkey": pubkey.export_key().decode(),
    }
    conn.send(dumps(dt).encode())

    dt = loads(cipher.decrypt(conn.recv(1024)))
    if dt["type"] != ppf.types.AES:
        conn.close()
        return
    
    return _load_cipher(dt["key"], dt["iv"])