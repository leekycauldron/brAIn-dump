from ollama import chat
import subprocess
import requests
import time
from pathlib import Path

class Client:
    def __init__(self, model: str) -> None:
        timeout = 20
        self.model = model
        self.context = [{"role": "system", "content": Path("prompt").read_text(encoding='utf-8').strip()}]
        self.process = subprocess.Popen(
            ["ollama", "run", model],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        # Wait until model is ready
        url = "http://localhost:11434/api/chat"
        for i in range(timeout):
            try:
                # Send a dummy chat to check readiness
                response = requests.post(url, json={
                    "model": model,
                    "messages": [{"role": "user", "content": "respond only with pong."}]
                }, timeout=2)

                if response.status_code == 200:
                    print(f"Ollama model '{model}' is ready.")
                    return
            except Exception:
                pass
            time.sleep(1)

        # Timeout
        self.process.terminate()
        raise TimeoutError(f"Ollama model '{model}' did not start within {timeout} seconds.")
    
    def run(self):
        try:
            while True:
                user_input = input("[User]: ")
                self.context.append({"role": "user", "content": user_input})
                stream = chat(
                    model = self.model,
                    messages=self.context,
                    stream=True
                )
                print("[AI]: ", end="")
                response = ""
                for chunk in stream:
                    response += chunk['message']['content'] 
                    print(chunk['message']['content'] , end="")
                print()
                self.context.append({"role": "assistant", "content": response})
        except Exception as e:
            print("Error:",e)
        finally:
            self.process.terminate()
            subprocess.run(['ollama', 'stop', self.model])


if __name__ == "__main__":
    c = Client("llama3.1:latest")
    c.run()