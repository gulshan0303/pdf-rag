from sqlalchemy.orm import Session

from app.models.document_chunk import DocumentChunk


class ChunkRepository:

    def __init__(self, db: Session):
        self.db = db

    def create_many(self, chunks: list[dict]) -> list[DocumentChunk]:

        chunk_objects = [
            DocumentChunk(**chunk)
            for chunk in chunks
        ]

        self.db.add_all(chunk_objects)

        return chunk_objects