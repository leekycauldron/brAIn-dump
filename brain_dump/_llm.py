from ollama import chat
import subprocess
import requests
import time
from pathlib import Path
from datetime import datetime
from typing import Optional
from brain_dump._indexer import Indexer
from brain_dump._models import Date
import os
import json
from jinja2 import Template


tools = [
    {
        "type": "function",
        "function": {
            "name": "query_rag_database",
            "description": "A query function to query a RAG database",
            "parameters": {
                "type": "object",
                "required": [
                    "collection",
                ],
                "properties": {
                    "collection": {
                        "type": "string",
                        "description": "A list of possible collections to choose from. 'media' for past journal entries",
                        "enum": ["media"]
                    },
                    "query": {
                        "type": "string",
                        "description": "Optional query to collection. This looks at the actual content."
                    },
                    "n": {
                        "type": "number",
                        "description": "Limit results to a positive integer, n. This is not the last n entries, it will be random."
                    },
                    "before": {
                        "type": "object",
                        "description": "Get entries that appear only before this date. Must be an object with year, month, and date fields. Do not use a string like '2025-07-07'.",
                        "properties": {
                            "year": {
                                "type": "number",
                                "description": "Year limit before"
                            },
                            "month": {
                                "type": "number",
                                "description": "Month limit before (1-12)"
                            },
                            "date": {
                                "type": "number",
                                "description": "Date limit before (1-31)"
                            }
                        },
                        "additionalProperties": False,
                        "required": [
                            "year",
                            "month",
                            "date"
                        ]
                    },
                    "after": {
                        "type": "object",
                        "description": "Date limit after the given date. Must be an object with year, month, and date fields. Do not use a string like '2025-07-07'.",
                        "properties": {
                        "year": {
                            "type": "number",
                            "description": "Year limit after"
                        },
                        "month": {
                            "type": "number",
                            "description": "Month limit after (1-12)"
                        },
                        "date": {
                            "type": "number",
                            "description": "Date limit after (1-31)"
                        }
                        },
                        "additionalProperties": False,
                        "required": [
                            "year",
                            "month",
                            "date"
                        ]
                    }
                },
                "additionalProperties": False
            }
        }
    }
    
]

def generate_dev_prompt():
    with open(os.path.join("brain_dump","prompt"), "r", encoding="utf-8") as f:
        template_str = f.read()

    template = Template(template_str)

    filled_prompt = template.render(
        current_time=datetime.now().strftime("%A %B %d %Y, %I:%M %p")
    )
    dir_path = Path(os.path.join("brain_dump","examples"))
    for file in dir_path.iterdir():
        if file.is_file():
            with open(file.resolve(),'r') as f:
                content = f.read()
            filled_prompt+=f"\n###\n{file.name}:\n{content}"
    print(filled_prompt)
    return filled_prompt

class Client:
    def __init__(self, model: str) -> None:
        timeout = 20
        self.model = model
        self.context = [{"role": "system", "content": generate_dev_prompt()}]
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
                }, timeout=5)

                if response.status_code == 200:
                    print(f"Ollama model '{model}' is ready.")
                    return
            except Exception as e:
                print(e)
            time.sleep(1)

        # Timeout
        self.process.terminate()
        raise TimeoutError(f"Ollama model '{model}' did not start within {timeout} seconds.")
    
    def chat(self, message: Optional[str] = None):
        if message:
            self.context.append({"role": "user", "content": message})
        response = chat(
            model = self.model,
            messages=self.context,
            tools=tools
        )
        print(response)
        if response.message.tool_calls:
            self.context.append(response["message"])
            # There may be multiple tool calls in the response
            for tool in response.message.tool_calls:
                # Ensure the function is available, and then call it
                print('Calling function:', tool.function.name)
                print('Arguments:', tool.function.arguments)
                if tool.function.name == "query_rag_database":
                    args = tool.function.arguments
                    i = Indexer(collection=str(args.get("collection")))
                    before = json.loads(args.get("before")) if type(args.get("before")) is str else args.get("before")
                    before_date = None
                    # There may be an error if using February and not date specify -> Feb 31 -> Doesn't Exist!
                    if before:
                        before_date = Date(year=before["year"], month=before["month"], day=before["date"])
                    after = json.loads(args.get("after")) if type(args.get("after")) is str else args.get("after")
                    after_date = None
                    if after:
                        after_date = Date(year=after["year"], month=after["month"], day=after["date"])
                    
                    output = i.query(
                        query=str(args.get("query")),
                        n=args.get("n"),
                        before=before_date,
                        after=after_date
                        )
                    print("Output:", output)
                    self.context.append({"role": "tool", "content": str(output), "name": tool.function.name})
            return self.chat()
        if response.message.content:
            self.context.append({"role": "assistant", "content": response['message']['content']})
            return response['message']['content']
        

    def close(self):
        self.process.terminate()
        subprocess.run(['ollama', 'stop', self.model])
    


if __name__ == "__main__":
    c = Client("command-r7b:latest")
    try:
        while True:
            print("[Assistant]:",c.chat(input("[User]: ")))
    except Exception as e:
        print("Error:",e)
    finally:
        c.close()