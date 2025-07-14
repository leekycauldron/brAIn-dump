import brain_dump


i = brain_dump.Indexer("media")
i.index()

c = brain_dump.Client("qwen3:14b")
try:
    while True:
        print("[Assistant]:",c.chat(input("[User]: ")))
except Exception as e:
    print("Error:",e)
finally:
    c.close()