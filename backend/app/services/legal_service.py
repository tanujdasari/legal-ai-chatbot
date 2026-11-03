from app.schemas.chat import ChatRequest, ChatResponse
from app.services.ai_service import generate_ai_answer
from app.rag.retriever import search_document


DISCLAIMER = (
    "This chatbot provides general legal information, not legal advice. "
    "Uploaded documents have not been independently verified. "
    "Consult a qualified lawyer for legal decisions."
)


def generate_legal_response(
    request: ChatRequest,
) -> ChatResponse:
    """
    Generate a legal AI response.

    If document_id is provided:
      1. Retrieve relevant PDF chunks.
      2. Build a context with page references.
      3. Send context to OpenAI.
      4. Return the answer and source references.
    """

    context = ""
    sources = []

    if request.document_id:
        results = search_document(
            document_id=request.document_id,
            question=request.question,
            jurisdiction=request.jurisdiction,
            top_k=4,
        )

        context_parts = []

        for index, result in enumerate(results, start=1):
            source_label = (
                f"[Excerpt {index}: "
                f"{result['filename']}, page {result['page']}]"
            )

            context_parts.append(
                f"{source_label}\n{result['text']}"
            )

            sources.append(source_label)

        context = "\n\n".join(context_parts)

    answer = generate_ai_answer(
        request=request,
        context=context,
    )

    return ChatResponse(
        answer=answer,
        jurisdiction=request.jurisdiction,
        category=request.category,
        state=request.state,
        sources=sources,
        disclaimer=DISCLAIMER,
        status=(
            "document_grounded_unverified"
            if request.document_id
            else "ai_generated_unverified"
        ),
    )