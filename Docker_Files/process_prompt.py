import sys
import json
import base64
from api import OllamaAPI
from config import Configuration
from encrypt_decrypt import Encryptor,Decryptor

def main():
    configuration = Configuration()
    decryptor = Decryptor(
        configuration.private_key_path,
        configuration.public_key_path
    )
    if len(sys.argv) < 4:
        return
    base_64_encoded_encrypted_message = sys.argv[1]
    base_64_encoded_encrypted_key = sys.argv[2]
    base_64_encoded_encrypted_iv = sys.argv[3]

    encrypted_message = base64.b64decode(base_64_encoded_encrypted_message)
    encrypted_key = base64.b64decode(base_64_encoded_encrypted_key)
    encrypted_iv = base64.b64decode(base_64_encoded_encrypted_iv)

    original = decryptor.decrypt_message(
        encrypted_message,
        encrypted_key,
        encrypted_iv
    )

    api = OllamaAPI()
    response = api.api_call(original)
    ai_reply = api.get_ai_response(response)
    encryptor = Encryptor(configuration.sender_public_key_path)
    ai_encrypted_reply,ai_encrypted_key,ai_encrypted_iv = encryptor.encrypt_message(ai_reply)
    base64_encoded_ai_encrypted_reply = base64.b64encode(ai_encrypted_reply).decode("ascii")
    base64_encoded_ai_encrypted_key = base64.b64encode(ai_encrypted_key).decode("ascii")
    base64_encoded_ai_encrypted_iv = base64.b64encode(ai_encrypted_iv).decode("ascii")
    print(json.dumps((base64_encoded_ai_encrypted_reply,base64_encoded_ai_encrypted_key,base64_encoded_ai_encrypted_iv)))

if __name__ == "__main__":
    main()
