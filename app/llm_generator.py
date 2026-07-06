import os
import requests
import logging



# Read API key from environment variable
API_KEY = os.getenv("DEEPSEEK_API_KEY")

API_URL = "https://api.deepseek.com/chat/completions"


def generate_test_cases(document_text):

    logger = logging.getLogger(__name__)

    if not API_KEY:
        logger.error(
            "[llm_generator] DEEPSEEK_API_KEY is not set. "
            "Returning stub YAML — this is NOT a real API response. "
            "Set DEEPSEEK_API_KEY in your .env file."
        )
        return """
test_cases:
  - id: TC001
    title: Login Test (STUB — API key missing)
    priority: High
    steps:
      - Open Login Page
      - Enter Username
      - Enter Password
      - Click Login
    expected_result: User logged in
"""

    prompt = f"""
Generate YAML test cases.

Return VALID YAML ONLY.

No markdown.
No explanation.

Structure:

test_cases:
  - id:
    title:
    priority:
    steps:
    expected_result:

Generate:
- positive cases
- negative cases
- edge cases

Document:

{document_text}
"""

    try:

        response = requests.post(
            API_URL,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0
            },
            timeout=120
        )

        if response.status_code != 200:
            return f"ERROR: {response.text}"

        result = response.json()

        return result["choices"][0]["message"]["content"]

    except Exception as e:

        return f"ERROR: {e}"