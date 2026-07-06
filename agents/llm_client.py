import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

# DeepSeek model identifiers (mid-2025):
#   deepseek-chat      — general purpose, fast, recommended default
#   deepseek-reasoner  — extended reasoning (R1), slower
# Docs: https://platform.deepseek.com/docs/models
DEEPSEEK_MODELS = ["deepseek-chat", "deepseek-reasoner"]


def get_llm(
    model: str = "deepseek-chat",   # was "deepseek-v4-flash" — does not exist
    temperature: float = 0.0,
) -> ChatOpenAI:
    """
    Returns a DeepSeek LLM via the OpenAI-compatible API.

    Args:
        model: deepseek-chat (default) or deepseek-reasoner.
        temperature: 0.0 = deterministic output.
    """
    if model not in DEEPSEEK_MODELS:
        print(
            f"[LLM Client] WARNING: '{model}' is not a known DeepSeek model. "
            f"Known: {DEEPSEEK_MODELS}. Falling back to 'deepseek-chat'."
        )
        model = "deepseek-chat"

    return ChatOpenAI(
        model=model,
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        temperature=temperature,
        max_retries=3,
    )