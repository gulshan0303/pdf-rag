import os

from dotenv import load_dotenv
from google import genai
from sqlalchemy.orm import Session

from app.services.retrieval_service import RetrievalService


load_dotenv()


class RAGService:

    def __init__(self, db: Session):
        self.retrieval_service = RetrievalService(db)

        api_key = os.getenv("GEMINI_API_KEY")
        model = os.getenv("LLM_MODEL")

        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not configured")

        if not model:
            raise RuntimeError("LLM_MODEL is not configured")

        self.client = genai.Client(api_key=api_key)
        self.model = model

    def answer(
        self,
        question: str,
        document_id: int,
        top_k: int = 5,
    ):

        results = self.retrieval_service.retrieve(
            question=question,
            document_id=document_id,
            top_k=top_k,
        )

        context_parts = []

        for chunk, distance in results:

            context_parts.append(
                f"""
[Page {chunk.page_number}]
[Chunk ID: {chunk.id}]
{chunk.content}
"""
            )

        context = "\n\n".join(context_parts)

        prompt = f"""
You are a document question-answering assistant.

Answer the user's question using ONLY the provided context.

Rules:
1. Do not use outside knowledge.
2. Do not invent information.
3. If the answer is not present in the context, clearly say that the information is not available in the document.
4. Keep the answer concise.
5. When possible, mention the relevant page number.

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:
"""

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )

        sources = [
            {
                "chunk_id": chunk.id,
                "page": chunk.page_number,
                "distance": float(distance),
            }
            for chunk, distance in results
        ]

        return {
            "answer": response.text,
            "sources": sources,
        }