import re
from pathlib import Path

import pymupdf
from sqlalchemy.orm import Session

from app.repositories.document_repository import DocumentRepository
from app.repositories.chunk_repository import ChunkRepository
from app.services.embedding_service import EmbeddingService


class IngestionService:

    def __init__(self, db: Session):
        self.db = db
        self.document_repository = DocumentRepository(db)
        self.chunk_repository = ChunkRepository(db)
        self.embedding_service = EmbeddingService()

    def extract_pages(self, pdf_path: str) -> list[dict]:
        path = Path(pdf_path)

        if not path.exists():
            raise FileNotFoundError(
                f"PDF not found: {pdf_path}"
            )

        document = pymupdf.open(pdf_path)

        pages = []

        try:
            for page_number, page in enumerate(document, start=1):
                text = page.get_text("text")

                pages.append({
                    "page_number": page_number,
                    "text": text,
                })

        finally:
            document.close()

        return pages

    def normalize_line(self, line: str) -> str:
        return re.sub(r"\s+", " ", line).strip()

    def remove_repeated_lines(
        self,
        pages: list[dict],
        min_occurrences: int = 2,
    ) -> list[dict]:

        line_counts = {}

        for page in pages:

            seen_on_page = set()

            for line in page["text"].splitlines():

                normalized = self.normalize_line(line)

                if not normalized:
                    continue

                if normalized in seen_on_page:
                    continue

                seen_on_page.add(normalized)

                line_counts[normalized] = (
                    line_counts.get(normalized, 0) + 1
                )

        repeated_lines = {
            line
            for line, count in line_counts.items()
            if count >= min_occurrences
        }

        cleaned_pages = []

        for page in pages:

            cleaned_lines = []

            for line in page["text"].splitlines():

                normalized = self.normalize_line(line)

                if normalized in repeated_lines:
                    continue

                cleaned_lines.append(line)

            cleaned_pages.append({
                "page_number": page["page_number"],
                "text": "\n".join(cleaned_lines),
            })

        return cleaned_pages

    def is_heading(self, text: str) -> bool:
        text = text.strip()

        if not text:
            return False

        # Example:
        # 2. Hiring Process
        # 5. Probation Policy
        # 8. Leave Policy
        if re.match(
            r"^\d+\.\s+[A-Za-z].{1,100}$",
            text
        ):
            return True

        # Explicitly support Introduction
        if text.lower() == "introduction:":
            return True

        return False

    def split_into_sections(
        self,
        text: str,
    ) -> list[dict]:

        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        sections = []

        current_heading = None
        current_lines = []

        for line in lines:

            if self.is_heading(line):

                if current_lines:
                    sections.append({
                        "heading": current_heading,
                        "content": "\n".join(current_lines),
                    })

                current_heading = line
                current_lines = []

            else:
                current_lines.append(line)

        if current_lines:
            sections.append({
                "heading": current_heading,
                "content": "\n".join(current_lines),
            })

        return sections

    def clean_text(self, text: str) -> str:
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n\s*\n+", "\n\n", text)

        return text.strip()

    def split_sentences(self, text: str) -> list[str]:

        sentences = re.split(
            r"(?<=[.!?])\s+",
            text,
        )

        return [
            sentence.strip()
            for sentence in sentences
            if sentence.strip()
        ]

    def chunk_section(
        self,
        heading: str | None,
        content: str,
        page_number: int,
        chunk_size: int = 1500,
    ) -> list[dict]:

        text = self.clean_text(content)

        sentences = self.split_sentences(text)

        chunks = []

        prefix = f"{heading}\n" if heading else ""

        current = prefix

        for sentence in sentences:

            proposed = (
                current
                + (" " if current else "")
                + sentence
            )

            if len(proposed) <= chunk_size:
                current = proposed

            else:

                if current.strip():
                    chunks.append(current.strip())

                current = prefix + sentence

        if current.strip():
            chunks.append(current.strip())

        return [
            {
                "content": chunk,
                "page_number": page_number,
                "section": heading,
            }
            for chunk in chunks
        ]

    def process_pdf(
        self,
        pdf_path: str,
    ) -> list[dict]:

        pages = self.extract_pages(pdf_path)

        pages = self.remove_repeated_lines(pages)

        all_chunks = []

        for page in pages:

            sections = self.split_into_sections(
                page["text"]
            )

            for section in sections:

                chunks = self.chunk_section(
                    heading=section["heading"],
                    content=section["content"],
                    page_number=page["page_number"],
                )

                all_chunks.extend(chunks)

        return all_chunks

    def ingest(
        self,
        pdf_path: str,
        filename: str,
        title: str | None = None,
    ):

        try:

            # 1. Create document
            document = self.document_repository.create(
                filename=filename,
                title=title,
            )

            # 2. Process PDF
            chunks = self.process_pdf(pdf_path)

            db_chunks = []

            # 3. Generate embeddings
            for index, chunk in enumerate(chunks):

                embedding = self.embedding_service.embed_text(
                    chunk["content"]
                )

                db_chunks.append({
                    "document_id": document.id,
                    "chunk_index": index,
                    "content": chunk["content"],
                    "page_number": chunk["page_number"],
                    "metadata_": {
                        "section": chunk["section"],
                    },
                    "embedding": embedding,
                })

            # 4. Save chunks
            self.chunk_repository.create_many(
                db_chunks
            )

            # 5. Update document
            document.total_pages = len(
                self.extract_pages(pdf_path)
            )

            document.status = "COMPLETED"

            # 6. Commit transaction
            self.db.commit()

            return document

        except Exception:
            self.db.rollback()
            raise