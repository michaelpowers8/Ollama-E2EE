import requests
import traceback
from config import Configuration

class OllamaAPI:
    def __init__(self):
        self.configuration = Configuration()

    def api_call(self, prompt:str, system_prompt:str=None) -> requests.Response|None:
        if not(isinstance(system_prompt, (str,type(None)))):
            self.configuration.logger.log_error(f"System prompt must be str or None type. Got type {type(system_prompt)}. No API call will be made.")
            return None

        if not(isinstance(prompt, str)):
            self.configuration.logger.log_error(f"Prompt must be str type. Got type {type(prompt)}. No API call will be made.")
            return None

        payload:dict[str,str|list[dict[str,str]]|bool] = {
            "model": self.configuration.ai_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "stream": self.configuration.stream
        }

        try:
            response:requests.Response = requests.post(self.configuration.api_url, json=payload)
            response.raise_for_status()
            return response
        except requests.HTTPError:
            self.configuration.logger.log_error(f"HTTP Error making API call to ollama. Official error: {traceback.format_exc()}")
            return None

    def get_ai_response(self, response:requests.Response):
        if response is None:
            return None

        if not(isinstance(response, requests.Response)):
            self.configuration.logger.log_error(f"Response was not requests.Response type. Got type {type(response)}. No response available.")
            return None

        data = response.json()
        if not(isinstance(data,dict)):
            self.configuration.logger.log_error(f"JSON data in response was not dict type. Got type {type(data)}. No response available.")
            return None
        
        if not("message" in data.keys()):
            self.configuration.logger.log_error(f"Response did not have required key \"message\". No response available.")
            return None
        
        message:dict[str,str] = data["message"]
        if not(isinstance(message,dict)):
            self.configuration.logger.log_error(f"Response has the required key \"message\". However, the message is not a dict type. Got type {type(message)}. No response available.")
            return None
        
        if not("content" in message.keys()):
            self.configuration.logger.log_error(f"Response has the required key \"message\" and is a dict type. However, the message is missing the required key \"content\". No response available.")
            return None
        
        response_content:str = message["content"]
        if not(isinstance(response_content,str)):
            self.configuration.logger.log_error(f"Response has the required key \"message\" and is a dict type. The message is has the required key \"content\". However, the contents of the reply are not str type. Got type {type(response_content)}. No response available.")
            return None
        return response_content
