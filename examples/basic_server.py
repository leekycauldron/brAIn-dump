import brain_dump


i = brain_dump.Indexer("media")
i.index()

try:
    brain_dump.server.serve("qwen2.5:14b")
except KeyboardInterrupt:
    pass
finally:
    print("Closing program...")
    brain_dump.server_client.client.close()