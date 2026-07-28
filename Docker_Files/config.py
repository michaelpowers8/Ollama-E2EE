import os
import json
import traceback
from logger_class import APILogger

REQUIRED_KEYS:dict[str,type] = {
    "API_URL": str, 
    "MODEL": str, 
    "STREAM": bool,
    "PRIVATE_KEY_PATH":str,
    "PUBLIC_KEY_PATH": str,
    "SENDER_PUBLIC_KEY_PATH": str
}

class Configuration:
    def __init__(self):
        self.filename = "/home/ubuntu/ollama_history_encryption/config.json"
        self.configuration = self._load_configuration()
        self._verify_configuration()
        self.api_url = self.configuration.get("API_URL")
        self.ai_model = self.configuration.get("MODEL")
        self.stream = self.configuration.get("STREAM")
        self.private_key_path = self.configuration.get("PRIVATE_KEY_PATH")
        self.public_key_path = self.configuration.get("PUBLIC_KEY_PATH")
        self.sender_public_key_path = self.configuration.get("SENDER_PUBLIC_KEY_PATH")
        self.logger = APILogger()

    def _load_configuration(self):
        if not(os.path.exists(self.filename)):
            raise FileNotFoundError(f"{self.filename} file not found. No configuration can be loaded.")
        try:
            with open(self.filename, 'r', encoding='utf-8') as file:
                configuration = json.load(file)
        except json.JSONDecodeError:
            print(f"Error loading {self.filename} into json object. No configuration will be returned. Official error: {traceback.format_exc()}")
            raise json.JSONDecodeError(traceback.format_exc())
        except OSError:
            print(f"Error opening {self.filename}. No configuration will be returned. Official error: {traceback.format_exc()}")
            raise OSError(traceback.format_exc())
        except Exception:
            print(f"General error occurred while loading configuration into json object. Official error: {traceback.format_exc()}")
            raise Exception(traceback.format_exc())
        return configuration
    
    def _verify_configuration(self):
        if not(isinstance(self.configuration,dict)):
            raise TypeError(f"Configuration must be dict type. Got type {type(self.configuration)}")
        missing_keys:list[str] = []
        invalid_key_types:list[str] = []
        for key,item in REQUIRED_KEYS.items():
            if not(key in self.configuration):
                missing_keys.append(key)
                continue
            if not(isinstance(self.configuration.get(key), item)):
                invalid_key_types.append(key)
            
        if missing_keys:
            raise KeyError(f"Configuration missing required key(s) {', '.join(missing_keys)}. Failed to verify configuration. Unable to run application.")
        if invalid_key_types:
            raise ValueError(f"Configuration has invalid types for key(s) {', '.join(invalid_key_types)}. Failed to verify configuration. Unable to run application.")
    
    def __str__(self):
        return f"Configuration with configuration {json.dumps(self.configuration,indent=4)}"
    
    def __repr__(self):
        return f"Configuration()"

    def __hash__(self):
        return hash(
            (
                self.filename, 
                self.configuration,
                self.api_url,
                self.ai_model,
                self.stream
            )
        )
