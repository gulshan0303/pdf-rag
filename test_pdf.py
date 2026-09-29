import fitz

pdf_path = "sample.pdf"
print("------>",pdf_path)
document = fitz.open(pdf_path)

print("Total pages:", len(document))

for page_number, page in enumerate(document):
    text = page.get_text("text")

    print(f"\n--- Page {page_number + 1} ---")
    print(text[:1000])

document.close()