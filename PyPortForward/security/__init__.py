from Crypto.Cipher import AES
from uuid import UUID
import base64

import PyPortForward as ppf

def encrypt(buffer, token):
    """Encrypt the buffer with AES."""
    cipher = AES.new(UUID(token).bytes, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(buffer)
    return base64.b64encode(cipher.nonce + tag + ciphertext)

def decrypt(buffer, token):
    """Decrypt the buffer with AES."""
    buffer = base64.b64decode(buffer)
    nonce, tag, ciphertext = buffer[:16], buffer[16:32], buffer[32:]
    cipher = AES.new(UUID(token).bytes, AES.MODE_EAX, nonce)
    return cipher.decrypt_and_verify(ciphertext, tag)
