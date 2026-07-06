import yaml


def validate_yaml(yaml_text):
    """
    Validate generated YAML for Playwright test generation.
    """

    errors = []

    # -------------------------------------------------
    # Empty response
    # -------------------------------------------------

    if not yaml_text or not yaml_text.strip():
        return {
            "valid": False,
            "errors": ["Empty YAML response"],
        }

    # -------------------------------------------------
    # Parse YAML
    # -------------------------------------------------

    try:
        data = yaml.safe_load(yaml_text)

    except yaml.YAMLError as e:
        return {
            "valid": False,
            "errors": [f"YAML Parse Error: {e}"],
        }

    # -------------------------------------------------
    # Root validation
    # -------------------------------------------------

    if not isinstance(data, dict):
        return {
            "valid": False,
            "errors": ["YAML root must be a dictionary."],
        }

    if "test_cases" not in data:
        return {
            "valid": False,
            "errors": ["Missing 'test_cases' section."],
        }

    test_cases = data["test_cases"]

    if not isinstance(test_cases, list):
        return {
            "valid": False,
            "errors": ["'test_cases' must be a list."],
        }

    if len(test_cases) == 0:
        return {
            "valid": False,
            "errors": ["No test cases found."],
        }

    # -------------------------------------------------
    # Test case validation
    # -------------------------------------------------

    seen_ids = set()

    for index, tc in enumerate(test_cases, start=1):

        if not isinstance(tc, dict):
            errors.append(f"Test case #{index} must be a dictionary.")
            continue

        tc_id = tc.get("id", f"UNKNOWN_{index}")

        # Duplicate IDs
        if tc_id in seen_ids:
            errors.append(f"Duplicate test case ID: {tc_id}")

        seen_ids.add(tc_id)

        # Required fields
        required_fields = [
            "id",
            "title",
            "priority",
            "steps",
            "expected_result",
        ]

        for field in required_fields:
            if field not in tc or tc[field] in (None, "", []):
                errors.append(f"{tc_id}: Missing '{field}'.")

        # Steps validation
        steps = tc.get("steps", [])

        if not isinstance(steps, list):
            errors.append(f"{tc_id}: 'steps' must be a list.")

        elif len(steps) == 0:
            errors.append(f"{tc_id}: Steps list is empty.")

        else:
            for step_num, step in enumerate(steps, start=1):

                if not isinstance(step, str):
                    errors.append(
                        f"{tc_id}: Step {step_num} must be a string."
                    )
                    continue

                if not step.strip():
                    errors.append(
                        f"{tc_id}: Step {step_num} is empty."
                    )

    # -------------------------------------------------
    # Final result
    # -------------------------------------------------

    return {
        "valid": len(errors) == 0,
        "errors": errors,
    }