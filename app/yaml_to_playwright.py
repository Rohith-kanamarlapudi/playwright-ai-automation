import yaml


def convert_yaml_to_playwright(yaml_text):

    code_lines = []

    unsupported = []

    # -----------------------------------
    # Empty YAML Check
    # -----------------------------------

    if not yaml_text or not yaml_text.strip():

        return {
            "code": "Empty YAML",
            "unsupported": [],
            "test_cases": []
        }

    # -----------------------------------
    # Parse YAML
    # -----------------------------------

    try:

        data = yaml.safe_load(yaml_text)

    except Exception as e:

        return {
            "code": f"Invalid YAML: {e}",
            "unsupported": [],
            "test_cases": []
        }

    # -----------------------------------
    # Validate Structure
    # -----------------------------------

    if not isinstance(data, dict):

        return {
            "code": "Invalid YAML structure",
            "unsupported": [],
            "test_cases": []
        }

    test_cases = data.get("test_cases", [])

    if not isinstance(test_cases, list):

        return {
            "code": "'test_cases' must be a list",
            "unsupported": [],
            "test_cases": []
        }

    # -----------------------------------
    # Convert Test Cases
    # -----------------------------------

    for tc in test_cases:

        if not isinstance(tc, dict):
            continue

        code_lines.append("")
        code_lines.append(
            f"# =================================="
        )
        code_lines.append(
            f"# {tc.get('id')} - {tc.get('title')}"
        )
        code_lines.append(
            f"# =================================="
        )

        steps = tc.get("steps", [])

        for step in steps:

            s = str(step).lower()

            # -----------------------------------
            # Navigation
            # -----------------------------------

            if (
                "open" in s
                or "navigate" in s
                or "go to" in s
                or "homepage" in s
                or "login page" in s
            ):

                if "login" in s:

                    code_lines.append(
                        'page.goto("/login")'
                    )

                elif "home" in s:

                    code_lines.append(
                        'page.goto("/")'
                    )

                else:

                    code_lines.append(
                        'page.goto("/page")'
                    )

            # -----------------------------------
            # Username
            # -----------------------------------

            elif (
                "username" in s
                or "user name" in s
            ):

                if "invalid" in s:

                    code_lines.append(
                        'page.fill("#username", "wrong_user")'
                    )

                else:

                    code_lines.append(
                        'page.fill("#username", "test_user")'
                    )

            # -----------------------------------
            # Password
            # -----------------------------------

            elif "password" in s:

                if "invalid" in s:

                    code_lines.append(
                        'page.fill("#password", "wrong_password")'
                    )

                else:

                    code_lines.append(
                        'page.fill("#password", "Password123")'
                    )

            # -----------------------------------
            # Search
            # -----------------------------------

            elif "search" in s:

                if (
                    "non-existent" in s
                    or "non existent" in s
                ):

                    code_lines.append(
                        'page.fill("#search", "unknown_book")'
                    )

                else:

                    code_lines.append(
                        'page.fill("#search", "python")'
                    )

                code_lines.append(
                    'page.click("#searchBtn")'
                )

            # -----------------------------------
            # Borrow
            # -----------------------------------

            elif "borrow" in s:

                code_lines.append(
                    'page.click("#borrowBtn")'
                )

            # -----------------------------------
            # Return
            # -----------------------------------

            elif "return" in s:

                code_lines.append(
                    'page.click("#returnBtn")'
                )

            # -----------------------------------
            # Add Book
            # -----------------------------------

            elif "add" in s and "book" in s:

                code_lines.append(
                    'page.click("#addBookBtn")'
                )

            # -----------------------------------
            # Delete Book
            # -----------------------------------

            elif "delete" in s:

                code_lines.append(
                    'page.click("#deleteBtn")'
                )

            # -----------------------------------
            # Edit / Update
            # -----------------------------------

            elif (
                "edit" in s
                or "update" in s
                or "modify" in s
            ):

                code_lines.append(
                    'page.click("#editBtn")'
                )

            # -----------------------------------
            # Save
            # -----------------------------------

            elif "save" in s:

                code_lines.append(
                    'page.click("#saveBtn")'
                )

            # -----------------------------------
            # Login Button
            # -----------------------------------

            elif (
                "login button" in s
                or "click login" in s
            ):

                code_lines.append(
                    'page.click("#loginBtn")'
                )

            # -----------------------------------
            # Generic Click
            # -----------------------------------

            elif "click" in s:

                code_lines.append(
                    'page.click("#button")'
                )

            # -----------------------------------
            # Unsupported
            # -----------------------------------

            else:

                unsupported.append(step)

        code_lines.append("")

    return {
        "code": "\n".join(code_lines),
        "unsupported": unsupported,
        "test_cases": test_cases
    }