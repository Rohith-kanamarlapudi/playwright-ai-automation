from agents.llm_client import get_llm

llm = get_llm()

response = llm.invoke(
    "Reply with exactly one sentence: DeepSeek V4 Flash is working."
)

print(response.content)