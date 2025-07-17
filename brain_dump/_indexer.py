import chromadb
import hashlib
import os
import json
from pathlib import Path
from datetime import datetime
from brain_dump._models import Date
from brain_dump._parser import Transcriber
from typing import Optional


class Indexer:
    def __init__(self, collection: str, transcribe_model: str = "medium"):
        self.chroma_client = chromadb.PersistentClient(path="database")
        self.collection_name = collection
        self.collection = self.chroma_client.get_or_create_collection(name=collection)
        self.transcriber = Transcriber(transcribe_model)

    def fingerprint(self, file_name: str, content: str):
        base = f"{file_name}{content}"
        return hashlib.sha256(base.encode("utf-8")).hexdigest()
    
    def get_fingerprints(self):
        os.makedirs("fingerprints", exist_ok=True)
        file_path = f"fingerprints/{self.collection_name}.json"
        Path(file_path).touch()
        if os.path.getsize(file_path) == 0:
            return {}
        with open(file_path, "r") as f:
            data = json.load(f)
        return data

    def index(self):
        cycle = {}
        os.makedirs(self.collection_name, exist_ok=True)
        dir_path = Path(self.collection_name)
        for file in dir_path.iterdir():
            if file.is_file():
                if file.name.endswith(('.gitkeep')):
                    continue
                print(f"Full path: {file.resolve()}")
                print(f"Filename : {file.name}")
                print("-" * 40)
                f_content = content = "" # f_content is used when using AI models to get content of audio or image. Its non deterministic nature means I can't use the output for the fingerprint.
                if file.name.endswith(".txt"):
                    with open(file.resolve(),'r') as f:
                       f_content = content = f.read() 
                if file.name.endswith((".mp3", ".wav")):
                    with open(file.resolve(), "rb") as f:
                        f_content = f.read()
                    content = self.transcriber.transcribe(str(file.resolve()))
                cycle[self.fingerprint(file.name, f_content)] = [file.name, content]
        fingerprints = self.get_fingerprints()
        print("Looped through dir, found: " + str(cycle))
        # Delete any old documents from index.
        for k in list(fingerprints.keys()):
            if k not in cycle:
                print(f"Document found in index, no longer found in {self.collection_name}, deleting from index...")
                self.collection.delete(ids=[k])
                del fingerprints[k]
        # Add any new documents to index and fingerprint database
        for k, v in cycle.items():
            if k not in fingerprints:
                print(f"New document detected in cycle, adding to index...")
                
                self.collection.add(
                    ids=[k],
                    documents=[v[1]], # 0 = filename, 1 = content
                    metadatas=[{
                        "timestamp": datetime.now().timestamp(),
                        "timestamp_read":datetime.now().strftime("%A %B %d %Y, %I:%M %p"),
                    }]
                )
                fingerprints[k] = v[0]
        # Rewrite fingerprints database.
        with open(f"fingerprints/{self.collection_name}.json", "w", encoding="utf-8") as f:
            json.dump(fingerprints, f, indent=4)

        self.transcriber.close()

    def query(self, query: str, n: int = 10, before: Optional[Date] = None, after: Optional[Date] = None):
        before_date = before
        if before is None:
            before_date = datetime.now()
        else:
            before_date = datetime(before.year, before.month, before.day)
        after_date = after
        if after is None:
            after_date = datetime(2,1,1)
        else:
            after_date = datetime(after.year, after.month, after.day)
        return self.collection.query(
            query_texts=[query],
            n_results=n,
            where={
                "$and": [
                    {"timestamp": {"$gte": after_date.timestamp()}},
                    {"timestamp": {"$lte": before_date.timestamp()}}
                ]
            }
        )