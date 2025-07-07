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

import brain_dump


i = brain_dump.Indexer("media")
i.index()

print(i.query("test",after=brain_dump.Date(year=2025,month=8,day=1)))