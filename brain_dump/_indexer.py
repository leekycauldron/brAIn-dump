import chromadb
import hashlib
import os
import json
from pathlib import Path
from datetime import datetime


class Indexer:
    def __init__(self, collection: str):
        self.chroma_client = chromadb.PersistentClient(path="database")
        self.collection_name = collection
        self.collection = self.chroma_client.get_or_create_collection(name=collection)

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
        cycle = {

        }
        os.makedirs(self.collection_name, exist_ok=True)
        dir_path = Path(self.collection_name)
        for file in dir_path.iterdir():
            if file.is_file():
                if file.name.endswith(('.gitkeep')):
                    continue
                print(f"Full path: {file.resolve()}")
                print(f"Filename : {file.name}")
                print("-" * 40)
                content = ""
                if file.name.endswith(".txt"):
                    with open(file.resolve(),'r') as f:
                       content = f.read() 
                cycle[self.fingerprint(file.name, content)] = [file.name, content]
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
                        "timestamp": datetime.now().strftime("%A %B %d %Y, %I:%M %p")
                    }]
                )
                fingerprints[k] = v[0]
        # Rewrite fingerprints database.
        with open(f"fingerprints/{self.collection_name}.json", "w", encoding="utf-8") as f:
            json.dump(fingerprints, f, indent=4)

    def query(self, query: str, n: int = 10):
        return self.collection.query(
            query_texts=[query],
            n_results=n
        )