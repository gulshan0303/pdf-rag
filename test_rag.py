from app.database.connection import SessionLocal
from app.services.rag_service import RAGService


db = SessionLocal()

try:

    service = RAGService(db)

    result = service.answer(
        question="What is the Confidentiality & Intellectual Property?",
        document_id=1,
        top_k=5,
    )

    print("\n================ ANSWER ================\n")
    print(result["answer"])

    print("\n================ SOURCES ================\n")

    for source in result["sources"]:
        print(source)

finally:
    db.close()