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

    prompt = f"""You are a QA automation engineer using Playwright.
Generate test cases for this application:

{document_text}

Return ONLY valid YAML in this EXACT structure — no other format accepted:

test_cases:
  - id: TC001
    title: Test login with valid credentials
    priority: High
    steps:
      - Open login page
      - Enter username
      - Enter password
      - Click login button
      - Verify dashboard is visible
    expected_result: User is redirected to dashboard

Rules:
- Each step must be a short, actionable phrase
- At least one step must start with "Verify" or "Assert"
- Use plain English action phrases (Open, Click, Enter, Verify, Navigate)
- Return ONLY YAML — no markdown fences, no explanation"""

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