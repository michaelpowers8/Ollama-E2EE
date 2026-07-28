import os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, padding as sym_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.serialization import (
    load_pem_private_key, load_pem_public_key,
    PrivateFormat, PublicFormat, Encoding, NoEncryption
)

class Encryptor:
    def __init__(self, public_key_path:str):
        self.public_key_path:str = public_key_path
        self.public_key = self._load_public_key()
        self.padder = padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )

    def _load_public_key(self):
        if not(os.path.exists(self.public_key_path)):
            return None
        
        with open(self.public_key_path, 'rb') as file:
            public_key_pem = file.read()
        public_key = load_pem_public_key(public_key_pem,backend=default_backend())

        return public_key

    def encrypt_message(self,message:str) -> tuple[bytes,bytes,bytes]:
        key:bytes = os.urandom(32)  # Generate a random 256-bit key
        iv:bytes = os.urandom(16)   # Generate a random 128-bit IV

        cipher:Cipher = Cipher(algorithms.AES256(key), modes.CBC(iv))
        encryptor = cipher.encryptor()

        padder = sym_padding.PKCS7(128).padder()  # 128 bits = 16 bytes
        padded_data = padder.update(message.encode()) + padder.finalize()

        ciphertext:bytes = encryptor.update(padded_data) + encryptor.finalize()

        encrypted_key = self.public_key.encrypt(
            key,
            padding=self.padder
        )
        encrypted_iv = self.public_key.encrypt(
            iv,
            padding=self.padder
        )

        return ciphertext, encrypted_key, encrypted_iv

class Decryptor:
    def __init__(self, private_key_path:str, public_key_path:str):
        self.private_key_path:str = private_key_path
        self.public_key_path = public_key_path
        self.padder = padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )

    def _load_private_key(self):
        if not(os.path.exists(self.private_key_path)):
            return self._create_and_save_keys()

        with open(self.private_key_path, 'rb') as file:
            private_key_pem = file.read()
        private_key = load_pem_private_key(private_key_pem,password=None,backend=default_backend())

        return private_key

    def _create_and_save_keys(self):
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        private_key_pem = private_key.private_bytes(
                encoding=Encoding.PEM,
                format=PrivateFormat.PKCS8,
                encryption_algorithm=NoEncryption()
            )

        public_key_pem = public_key.public_bytes(
                encoding=Encoding.PEM,
                format=PublicFormat.PKCS1
            )
        
        with open(self.private_key_path, "wb") as file:
            file.write(private_key_pem)
        with open(self.public_key_path, "wb") as file:
            file.write(public_key_pem)

        return private_key

    def decrypt_message(self,
        encrypted_message:bytes, 
        encrypted_key:bytes, 
        encrypted_iv:bytes
    ) -> str:
        key = self._load_private_key().decrypt(
            encrypted_key,
            padding=self.padder
        )
        iv = self._load_private_key().decrypt(
            encrypted_iv,
            padding=self.padder
        )

        cipher:Cipher = Cipher(algorithms.AES256(key), modes.CBC(iv))
        decryptor = cipher.decryptor()
        padded_message:bytes = decryptor.update(encrypted_message) + decryptor.finalize()

        unpadder = sym_padding.PKCS7(128).unpadder()  # 128 bits = 16 bytes block size
        message: bytes = unpadder.update(padded_message) + unpadder.finalize()
        return message.decode('utf-8')
