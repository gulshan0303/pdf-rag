from pathlib import Path

import pymupdf


class IngestionService:

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