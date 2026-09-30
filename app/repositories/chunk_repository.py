from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document_chunk import DocumentChunk


class ChunkRepository:

    def __init__(self, db: Session):
        self.db = db

    def create_many(self, chunks: list[dict]):
        chunk_objects = [
            DocumentChunk(**chunk)
            for chunk in chunks
        ]

        self.db.add_all(chunk_objects)

        return chunk_objects

    def search_similar(
        self,
        query_embedding: list[float],
        document_id: int,
        top_k: int = 5,
    ):
        distance = DocumentChunk.embedding.cosine_distance(
            query_embedding
        )

        statement = (
            select(
                DocumentChunk,
                distance.label("distance"),
            )
            .where(
                DocumentChunk.document_id == document_id
            )
            .order_by(distance)
            .limit(top_k)
        )

        return self.db.execute(statement).all()