import pymupdf

from app.services.text_processing import (
    chunk_page,
    remove_repeated_lines,
)


pdf_path = "sample.pdf"

document = pymupdf.open(pdf_path)

pages = []

for page in document:
    pages.append(
        page.get_text("text")
    )

document.close()


# Remove repeated headers/footers
pages = remove_repeated_lines(pages)


all_chunks = []

for page_number, page_text in enumerate(pages):

    page_chunks = chunk_page(
        text=page_text,
        page_number=page_number + 1,
        chunk_size=1500,
        overlap=200,
    )

    all_chunks.extend(page_chunks)


print("Total chunks:", len(all_chunks))


for index, chunk in enumerate(all_chunks):

    print(f"\n===== CHUNK {index} =====")

    print(
        "Page:",
        chunk["page_number"]
    )

    print(
        "Characters:",
        len(chunk["content"])
    )

    print(chunk["content"][:800])