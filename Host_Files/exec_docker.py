import json
import base64
import subprocess
from config import Configuration
from encrypt_decrypt import Encryptor,Decryptor

class Application:
    def __init__(self):
        self.configuration = Configuration()
        self.encryptor = Encryptor(self.configuration.recipient_public_key_path)
        self.decryptor = Decryptor(
            self.configuration.private_key_path,
            self.configuration.public_key_path
        )
    
    def answer_prompt(self,prompt:str):
        encrypted_message,encrypted_key,encrypted_iv = self.encryptor.encrypt_message(prompt)

        b64_message = base64.b64encode(encrypted_message).decode('utf-8')
        b64_key = base64.b64encode(encrypted_key).decode('utf-8')
        b64_iv = base64.b64encode(encrypted_iv).decode('utf-8')

        command = [
            "sudo", 
            "docker", 
            "exec", 
            self.configuration.container_name, 
            self.configuration.docker_python_path,
            self.configuration.docker_script_processor,
            b64_message,
            b64_key,
            b64_iv
        ]

        result = subprocess.run(command,capture_output=True, check=True)
        data = json.loads(result.stdout)
        base_64_encrypted_ai_reply = data[0]
        base_64_encrypted_ai_key = data[1]
        base_64_encrypted_ai_iv = data[2]

        ai_encrypted_reply = base64.b64decode(base_64_encrypted_ai_reply)
        ai_encrypted_key = base64.b64decode(base_64_encrypted_ai_key)
        ai_encrypted_iv = base64.b64decode(base_64_encrypted_ai_iv)

        reply = self.decryptor.decrypt_message(
            ai_encrypted_reply,
            ai_encrypted_key,
            ai_encrypted_iv
        )

        return reply

def main():
    app = Application()
    divider = f"""\n{"="*50}\n"""
    while True:
        prompt:str = input("ALL PROMPTS ARE END TO END ENCRYPTED AND INDEPENDENT FROM EACH OTHER.\nAsk AI anything securely.\n\n")
        answer = app.answer_prompt(prompt)
        print(f"""{divider}{answer}{divider}""")

if __name__ == "__main__":
    main()