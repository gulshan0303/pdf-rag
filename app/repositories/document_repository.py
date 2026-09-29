from sqlalchemy.orm import Session

from app.models.document import Document


class DocumentRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        filename: str,
        title: str | None = None,
    ) -> Document:

        document = Document(
            filename=filename,
            title=title,
            status="PROCESSING",
        )

        self.db.add(document)
        self.db.flush()

        return document