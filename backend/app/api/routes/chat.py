import logging

from fastapi import APIRouter, HTTPException
from openai import (
    AuthenticationError,
    RateLimitError,
    APITimeoutError,
    APIConnectionError,
    APIStatusError,
)

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.legal_service import generate_legal_response

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api",
    tags=["Legal Chat"],
)


@router.post("/chat", response_model=ChatResponse)
def legal_chat(request: ChatRequest):
    try:
        return generate_legal_response(request)
    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail="Document not found. Upload it again.",
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:
        logger.error("Chat configuration or response error: %s", exc)
        raise HTTPException(
            status_code=503,
            detail="AI service is not ready.",
        ) from exc

    except AuthenticationError as exc:
        logger.error("OpenAI authentication failed")
        raise HTTPException(
            status_code=503,
            detail="AI service authentication failed.",
        ) from exc

    except RateLimitError as exc:
        raise HTTPException(
            status_code=429,
            detail="AI service rate limit reached.",
        ) from exc

    except (APITimeoutError, APIConnectionError) as exc:
        raise HTTPException(
            status_code=503,
            detail="AI service temporarily unavailable.",
        ) from exc

    except APIStatusError as exc:
        logger.error(
            "OpenAI upstream status: %s",
            exc.status_code,
        )
        raise HTTPException(
            status_code=502,
            detail="AI provider returned an error.",
        ) from exc