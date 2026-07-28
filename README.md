# Ollama-E2EE

End-to-end encrypted (E2EE) bridge between a host machine and an Ollama instance running inside a Docker container.

Prompts leave the host encrypted. Only the container (which holds the corresponding private key) can decrypt them, call Ollama, encrypt the reply, and send it back. The host then decrypts the reply with its own private key.

This is an early-development proof-of-concept.

## How it works

1. Host generates a random AES-256 key + IV.
2. Prompt is encrypted with AES-256-CBC.
3. The AES key and IV are encrypted under the container’s RSA-4096 public key (OAEP-SHA256).
4. The three blobs (ciphertext, encrypted key, encrypted IV) are base64-encoded and passed to a script inside the container via `docker exec`.
5. Container decrypts the key/IV with its private key, decrypts the prompt, and sends it to Ollama (`http://localhost:11434`).
6. Ollama’s reply is encrypted the same way (new random AES key/IV) under the **host’s** public key.
7. The three blobs are returned as JSON; the host decrypts and displays the reply.

Every message uses a fresh AES key and IV. Private keys never leave their respective environments.

## Requirements

### Host
- Python **3.12+**
- `cryptography` library
- Docker (with permission to run `docker exec`, currently via `sudo`)
- A running Docker container that contains the `Docker_Files` and an Ollama instance

### Container
- Python **3.12+**
- `cryptography` and `requests`
- Ollama running and reachable at the URL configured in `config.json` (normally `http://localhost:11434`)

```bash
# Both environments
pip install cryptography requests