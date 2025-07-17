import brain_dump


#i = brain_dump.Indexer("media", "small")
#i.index()

try:
    brain_dump.server.serve("llama3.2")
except KeyboardInterrupt:
    pass
finally:
    print("Closing program...")
    brain_dump.server_client.client.close()