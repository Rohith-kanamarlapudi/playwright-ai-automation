import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()


def get_llm(
    model: str = "deepseek-v4-flash",
    temperature: float = 0.0,
):
    """
    Returns a DeepSeek V4 Flash LLM instance.
    """

    return ChatOpenAI(
        model=model,
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        temperature=temperature,
        max_retries=3,
    )