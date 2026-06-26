import os
import time
import csv
import requests

# Read the DeepSeek API key from the environment variable
API_KEY = os.getenv("DEEPSEEK_API_KEY")

if not API_KEY:
    print("Error: DEEPSEEK_API_KEY environment variable not found.")
    exit()

# Official DeepSeek API endpoint
URL = "https://api.deepseek.com/chat/completions"

# Sample Design Document
design_document = """
Project: Online Library Management System

The system allows students to search books, borrow books, and return books.
Librarians can add, update, and remove books.
Users should log in before borrowing books.
The system should keep track of available copies.
Notifications should be sent when borrowed books become overdue.
The application should be simple, secure, and easy to maintain.
"""

# Three different prompt styles
prompts = [
    (
        "Simple Prompt",
        "Read the following design document and summarize it.\n\nDesign Document:\n"
        + design_document
    ),
    (
        "Detailed Prompt",
        "You are a software architect.\n\n"
        "Read the following design document and provide:\n"
        "1. Summary\n"
        "2. Main Functional Requirements\n"
        "3. Non-functional Requirements\n"
        "4. Possible Improvements\n\n"
        "Design Document:\n"
        + design_document
    ),
    (
        "Step-by-Step Prompt",
        "Read the following design document carefully.\n\n"
        "Step 1: Summarize the project.\n"
        "Step 2: List the functional requirements.\n"
        "Step 3: List the non-functional requirements.\n"
        "Step 4: Suggest two improvements.\n\n"
        "Design Document:\n"
        + design_document
    )
]

# Output CSV file
csv_file = "benchmark_results.csv"

# Create CSV file
with open(csv_file, "w", newline="", encoding="utf-8") as file:

    writer = csv.writer(file)

    # CSV Header
    writer.writerow([
        "Prompt Style",
        "Response Time",
        "Input Tokens",
        "Output Tokens",
        "Quality Notes"
    ])

    # Test each prompt
    for style, prompt in prompts:

        print("=" * 60)
        print("Running:", style)

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        # Start timer
        start = time.time()

        response = requests.post(
            URL,
            headers=headers,
            json=data
        )

        # End timer
        end = time.time()

        response_time = end - start

        if response.status_code == 200:

            result = response.json()

            # Model response
            reply = result["choices"][0]["message"]["content"]

            # Token usage
            usage = result.get("usage", {})

            input_tokens = usage.get("prompt_tokens", "")
            output_tokens = usage.get("completion_tokens", "")

            # Print benchmark details
            print("Prompt Style :", style)
            print("Response Time:", round(response_time, 2), "seconds")
            print("Input Tokens :", input_tokens)
            print("Output Tokens:", output_tokens)

            print("\nResponse:\n")
            print(reply)

            # -----------------------------
            # Basic Automatic Quality Check
            # -----------------------------
            quality_note = "OK"

            if len(reply) < 100:
                quality_note = "Too short - check prompt"
            elif any(word in reply.lower() for word in ["summary", "requirement", "improvement"]):
                quality_note = "Relevant output"

            # Save results to CSV
            writer.writerow([
                style,
                round(response_time, 2),
                input_tokens,
                output_tokens,
                quality_note
            ])

        else:
            print("Request failed!")
            print("Status Code:", response.status_code)
            print(response.text)

print("\nBenchmark completed successfully!")
print("Results saved to benchmark_results.csv")