# Check to see if medical documents are all properly indexed.
# Run indexer (Collect fingerprints, and index)
# Initialize LLM conversation terminal (Create a tool to end conversation as well as allow user to save)
# Save conversation and index it.


# TODO: Connect tools to LLM for getting data.
# TODO: Create a way for the LLM to focus more on the most recent (same day) entries and work with that (should be a simply metadata filter)
# TODO: Add conversation to RAG
# TODO: Multi-Modal Media
# TODO: Empty conversation starter, end call tool
# TODO: Medical Knowledge?
# TODO: Setup scripts (to install ollama and make sure libraries are installed)
# TODO: Change README so anyone can run and customize
# TODO: Smart auto entry? (i talk about how last year something happened, automatically create a entry with the timestamp being a year ago)
# TODO: Create a logger + web interface for clean conversations/
# TODO: Create journaller interface for autonaming + tagging.
import brain_dump


i = brain_dump.Indexer("media")
i.index()

c = brain_dump.Client("llama3.2")
try:
    while True:
        print("[Assistant]:",c.chat(input("[User]: ")))
except Exception as e:
    print("Error:",e)
finally:
    c.close()