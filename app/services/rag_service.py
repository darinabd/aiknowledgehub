import math
import os
from typing import List, Dict, Any

from dotenv import load_dotenv
from openai import OpenAI

from app.models.chunk import DocumentChunk



load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not set")

client = OpenAI(api_key=OPENAI_API_KEY)

EMBEDDING_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4.1-mini"


def cosine_similarity(vector_a: List[float], vector_b: List[float]) -> float:
    dot_product = sum(a * b for a, b in zip(vector_a, vector_b))

    magnitude_a = math.sqrt(sum(a * a for a in vector_a))
    magnitude_b = math.sqrt(sum(b * b for b in vector_b))

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)


def create_embeddings(texts: List[str]) -> List[List[float]]:
    if not texts:
        return []

    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts,
    )

    return [item.embedding for item in response.data]


def find_relevant_chunks(
    question: str,
    chunks: List[DocumentChunk],
    limit: int = 5,
) -> List[Dict[str, Any]]:
    if not chunks:
        return []

    question_embedding = create_embeddings([question])[0]

    chunk_texts = [chunk.content for chunk in chunks]
    chunk_embeddings = create_embeddings(chunk_texts)

    scored_chunks = []

    for chunk, embedding in zip(chunks, chunk_embeddings):
        score = cosine_similarity(
            question_embedding,
            embedding,
        )

        scored_chunks.append(
            {
                "chunk_index": chunk.chunk_index,
                "content": chunk.content,
                "score": score,
            }
        )

    scored_chunks.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return scored_chunks[:limit]


def generate_answer(
    question: str,
    relevant_chunks: List[Dict[str, Any]],
) -> str:
    if not relevant_chunks:
        return "В документе не найдено информации для ответа на этот вопрос."

    context_parts = []

    for chunk in relevant_chunks:
        context_parts.append(
            f"[Фрагмент {chunk['chunk_index']}]\n"
            f"{chunk['content']}"
        )

    context = "\n\n".join(context_parts)

    response = client.responses.create(
        model=CHAT_MODEL,
        instructions=(
            "Ты — помощник для анализа документов. "
            "Отвечай только на основе предоставленного контекста. "
            "Не придумывай факты. "
            "Если в контексте нет ответа, прямо скажи, что информация "
            "не найдена в документе. "
            "Отвечай на языке вопроса пользователя."
        ),
        input=(
            f"Контекст документа:\n\n{context}\n\n"
            f"Вопрос пользователя:\n{question}"
        ),
    )

    return response.output_text

def generate_document_summary(chunks: List[DocumentChunk]) -> str:
    if not chunks:
        return "Документ не содержит текста."

    selected_chunks = chunks[:15]

    context = "\n\n".join(
        chunk.content for chunk in selected_chunks
    )

    response = client.responses.create(
        model=CHAT_MODEL,
        instructions=(
            "Ты анализируешь документы. "
            "Создай понятное краткое содержание документа. "
            "Выдели основную тему, ключевые идеи и выводы. "
            "Не добавляй информацию, которой нет в документе. "
            "Отвечай на языке документа."
        ),
        input=context,
    )

    return response.output_text


def generate_document_questions(
    chunks: List[DocumentChunk],
    amount: int = 5,
) -> str:
    if not chunks:
        return "Документ не содержит текста."

    selected_chunks = chunks[:15]

    context = "\n\n".join(
        chunk.content for chunk in selected_chunks
    )

    response = client.responses.create(
        model=CHAT_MODEL,
        instructions=(
            f"На основе документа создай {amount} вопросов "
            "для самопроверки. "
            "После каждого вопроса напиши краткий правильный ответ. "
            "Не используй информацию вне документа. "
            "Отвечай на языке документа."
        ),
        input=context,
    )

    return response.output_text