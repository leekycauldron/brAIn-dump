# Check to see if medical documents are all properly indexed.
# Run indexer (Collect fingerprints, and index)
# Initialize LLM conversation terminal (Create a tool to end conversation as well as allow user to save)
# Save conversation and index it.
import brain_dump


i = brain_dump.Indexer("media")
i.index()

print(i.query("test"))