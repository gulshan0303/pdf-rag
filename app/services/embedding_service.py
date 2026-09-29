import os

from dotenv import load_dotenv
from google import genai


load_dotenv()


class EmbeddingService:

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        model = os.getenv("EMBEDDING_MODEL")

        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured"
            )

        if not model:
            raise RuntimeError(
                "EMBEDDING_MODEL is not configured"
            )

        self.client = genai.Client(
            api_key=api_key
        )

        self.model = model

    def embed_text(self, text: str) -> list[float]:

        response = self.client.models.embed_content(
            model=self.model,
            contents=text,
        )

        return response.embeddings[0].values