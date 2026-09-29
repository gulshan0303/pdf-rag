from app.services.embedding_service import EmbeddingService


service = EmbeddingService()

text = """
2. Hiring Process

Initial Screening
Task Assignment
Final Evaluation
Offer Discussion
"""

embedding = service.embed_text(text)

print("Dimension:", len(embedding))
print("First 5 values:", embedding[:5])