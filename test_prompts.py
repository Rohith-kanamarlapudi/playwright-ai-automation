from agents.llm_client import get_llm
from agents.prompts.strategy_prompt import STRATEGY_PROMPT

llm = get_llm()

sample_doc = """
A user login page with:
- Username text input (id='username')
- Password text input (id='password')
- Submit button (id='login-btn')
- Error message div (class='error-msg')
"""

buttons = [
    {"id": "login-btn", "text": "Login"}
]

inputs = [
    {"id": "username", "type": "text"},
    {"id": "password", "type": "password"}
]

links = []

prompt = STRATEGY_PROMPT.format(
    design_doc=sample_doc,
    buttons=buttons,
    inputs=inputs,
    links=links
)

response = llm.invoke(prompt)

print("\n===== OUTPUT =====\n")
print(response.content if hasattr(response, "content") else response)