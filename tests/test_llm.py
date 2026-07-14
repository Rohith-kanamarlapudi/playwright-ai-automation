"""Unit test: verify the LLM client initialises and responds."""
import pytest
from agents.llm_client import get_llm


def test_llm_client_initialises():
    """get_llm() should return a ChatOpenAI instance without crashing."""
    llm = get_llm()
    assert llm is not None
    assert llm.model_name == "deepseek-chat"


@pytest.mark.skipif(
    not __import__("os").getenv("DEEPSEEK_API_KEY"),
    reason="DEEPSEEK_API_KEY not set — skipping live API call"
)
def test_llm_live_response():
    """Live API call — only runs when DEEPSEEK_API_KEY is set."""
    llm = get_llm()
    response = llm.invoke("Reply with exactly: OK")
    assert response.content.strip() != ""