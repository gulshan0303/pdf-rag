from app.database.connection import SessionLocal
from app.services.ingestion_service import IngestionService


db = SessionLocal()

try:
    service = IngestionService(db)

    document = service.ingest(
        pdf_path="sample.pdf",
        filename="sample.pdf",
        title="Limelight HR Policy",
    )

    print("Document ID:", document.id)
    print("Status:", document.status)
    print("Total pages:", document.total_pages)

finally:
    db.close()