from app.ingestion.pdf import process_pdf
from app.embeddings.embedder import embedder
from app.embeddings.vector_store import vector_store

# Change this to a real PDF path on your machine
PDF_PATH = "uploads/sample.pdf"

result = process_pdf(PDF_PATH, "sample.pdf")
print(f"Source ID: {result['source_id']}")
print(f"Number of chunks: {len(result['chunks'])}")
print(f"First chunk preview:\n{result['chunks'][0][:200]}")
print(f"First chunk metadata: {result['metadatas'][0]}")

# Embed and store
vectors = embedder.embed_texts(result["chunks"])
ids = [f"{result['source_id']}-{i}" for i in range(len(result["chunks"]))]

vector_store.add_chunks(
    ids=ids,
    embeddings=vectors,
    documents=result["chunks"],
    metadatas=result["metadatas"],
)

print("\nStored successfully. Testing retrieval...")
query_vec = embedder.embed_query("What is this document about?")
results = vector_store.query(query_embedding=query_vec, top_k=3)
for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
    print(f"\n[{meta['file']} p.{meta['page']}] {doc[:150]}")