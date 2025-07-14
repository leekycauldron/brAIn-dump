import brain_dump


i = brain_dump.Indexer("media")
i.index()

try:
    brain_dump.server.serve("qwen3:14b")
except KeyboardInterrupt:
        print("Closing program...")
        brain_dump.server_client.client.close()
