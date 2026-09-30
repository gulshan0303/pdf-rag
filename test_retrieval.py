from app.database.connection import SessionLocal
from app.services.retrieval_service import RetrievalService


db = SessionLocal()

try:
    service = RetrievalService(db)

    results = service.retrieve(
        question="How many annual leaves are available?",
        document_id=1,
        top_k=5,
    )

    for chunk, distance in results:
        print("\n-------------------------")
        print("Chunk ID:", chunk.id)
        print("Page:", chunk.page_number)
        print("Distance:", distance)
        print("Section:", chunk.metadata_)
        print("Content:", chunk.content)

finally:
    db.close()