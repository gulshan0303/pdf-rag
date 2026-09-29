import os

from dotenv import load_dotenv
from google import genai


load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = os.getenv("EMBEDDING_MODEL")

response = client.models.embed_content(
    model=model,
    contents="Employees get 18 annual leaves."
)
print(response)
embedding = response.embeddings[0].values

print("Model:", model)
print("Dimension:", len(embedding))
print("First 5 values:", embedding[:5])