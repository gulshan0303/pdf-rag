from app.services.ingestion_service import IngestionService
from app.services.embedding_service import EmbeddingService


ingestion_service = IngestionService()
embedding_service = EmbeddingService()

chunks = ingestion_service.process_pdf("sample.pdf")

print("Total chunks:", len(chunks))

for index, chunk in enumerate(chunks[:3]):

    embedding = embedding_service.embed_text(
        chunk["content"]
    )

    print("\n-----------------------------")
    print("Chunk:", index)
    print("Page:", chunk["page_number"])
    print("Section:", chunk["section"])
    print("Text:", chunk["content"][:200])
    print("Embedding dimension:", len(embedding))
    print("First 5 values:", embedding[:5])