"""Input sanitization for user-provided text.

Prevents prompt injection by stripping sequences that could manipulate
Claude's behavior when user input is embedded in prompts.
"""

import re

from app.core.logging import get_logger

logger = get_logger("sanitize")

# Patterns that could be used for prompt injection
_INJECTION_PATTERNS = [
    # System/assistant role manipulation
    re.compile(r"<\s*/?\s*(system|assistant|human)\s*>", re.IGNORECASE),
    # XML-style injection tags
    re.compile(r"<\s*/?\s*(instructions?|rules?|prompt)\s*>", re.IGNORECASE),
    # "Ignore previous instructions" style attacks
    re.compile(
        r"(?:ignore|disregard|forget|override)\s+(?:all\s+)?(?:previous|above|prior)\s+(?:instructions?|rules?|prompts?)",
        re.IGNORECASE,
    ),
    # "You are now" role reassignment
    re.compile(r"you\s+are\s+now\s+(?:a|an|my)\s+", re.IGNORECASE),
    # Attempts to set new system prompts
    re.compile(r"new\s+(?:system\s+)?(?:prompt|instructions?|rules?):", re.IGNORECASE),
]

# Max length for user free-text input
MAX_MESSAGE_LENGTH = 2000
MAX_DEALBREAKER_LENGTH = 100
MAX_NAME_LENGTH = 50


def sanitize_user_message(text: str | None) -> str | None:
    """Sanitize free-text user messages before embedding in Claude prompts."""
    if not text:
        return text

    cleaned = text[:MAX_MESSAGE_LENGTH].strip()

    for pattern in _INJECTION_PATTERNS:
        if pattern.search(cleaned):
            logger.warning(
                "prompt_injection_attempt",
                pattern=pattern.pattern[:50],
                input_preview=cleaned[:80],
            )
            cleaned = pattern.sub("[filtered]", cleaned)

    return cleaned


def sanitize_name(name: str) -> str:
    """Sanitize user display names."""
    return name[:MAX_NAME_LENGTH].strip()


def sanitize_dealbreakers(items: list[str]) -> list[str]:
    """Sanitize dealbreaker items."""
    return [item[:MAX_DEALBREAKER_LENGTH].strip() for item in items[:20]]


def sanitize_genres(genres: list[str]) -> list[str]:
    """Sanitize genre lists — only allow alphanumeric + spaces/hyphens."""
    clean = []
    for g in genres[:30]:
        cleaned = re.sub(r"[^a-zA-Z0-9\s\-]", "", g[:50]).strip()
        if cleaned:
            clean.append(cleaned)
    return clean
