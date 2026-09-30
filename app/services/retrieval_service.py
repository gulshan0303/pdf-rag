from sqlalchemy.orm import Session

from app.repositories.chunk_repository import ChunkRepository
from app.services.embedding_service import EmbeddingService


class RetrievalService:

    def __init__(self, db: Session):
        self.chunk_repository = ChunkRepository(db)
        self.embedding_service = EmbeddingService()

    def retrieve(
        self,
        question: str,
        document_id: int,
        top_k: int = 5,
    ):
        query_embedding = self.embedding_service.embed_text(
            question
        )

        results = self.chunk_repository.search_similar(
            query_embedding=query_embedding,
            document_id=document_id,
            top_k=top_k,
        )

        return results