import json
from pathlib import Path

import anthropic

from app.core.config import settings
from app.schemas.recommendation import RecommendationRequest

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def _load_system_prompt() -> str:
    return (PROMPTS_DIR / "filmmatch_system.md").read_text()


async def get_recommendation(request: RecommendationRequest) -> str:
    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    user_message = (
        request.message
        if request.message
        else json.dumps(request.model_dump(exclude_none=True), indent=2)
    )

    response = await client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=1024,
        system=_load_system_prompt(),
        messages=[{"role": "user", "content": user_message}],
    )

    return response.content[0].text
