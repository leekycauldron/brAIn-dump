from fastapi import FastAPI
from fastapi.responses import FileResponse
from brain_dump._llm import Client
from pydantic import BaseModel
import uvicorn
import os
import json

class ChatInput(BaseModel):
    message: str


class ServerClient():
    def __init__(self) -> None:
        self.client = None
        self.debug = False

client = ServerClient()
app = FastAPI()


@app.get("/")
def read_root():
    # Get the directory where this module is located
    module_dir = os.path.dirname(os.path.abspath(__file__))
    public_dir = os.path.join(module_dir, "static")
    index_path = os.path.join(public_dir, "index.html")
    
    return FileResponse(index_path)

@app.post("/chat")
def chat_with_ai(user_message: ChatInput):
    """
    Endpoint to chat with the AI art designer.
    Takes a user message and returns an AI response.
    """
    try:
        # Get response from the AI
        ai_response = client.client.chat(user_message.message)
        return ai_response
    except Exception as e:
        return f"Error: {e}. Payload received: {user_message}"

def serve(model):
    client.client = Client(model=model)
    # Run the server (no reload with class approach)
    uvicorn.run("brain_dump._server:app", host="127.0.0.1", port=8000, reload=False)
    