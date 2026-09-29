from app.services.ingestion_service import IngestionService


service = IngestionService()

pages = service.extract_pages("sample.pdf")

print("Total pages:", len(pages))

for page in pages:
    print("\n--- PAGE", page["page_number"], "---")
    print(page["text"][:500])