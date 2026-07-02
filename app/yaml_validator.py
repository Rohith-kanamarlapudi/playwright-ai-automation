import yaml


def validate_yaml(yaml_text):

    errors = []

    # Empty response check
    if not yaml_text or not yaml_text.strip():
        return {
            "valid": False,
            "errors": ["Empty YAML response"]
        }

    try:

        data = yaml.safe_load(yaml_text)

    except Exception as e:

        return {
            "valid": False,
            "errors": [f"YAML Parse Error: {e}"]
        }

    # Ensure YAML root is a dictionary
    if not isinstance(data, dict):

        return {
            "valid": False,
            "errors": [
                "YAML root must contain 'test_cases'"
            ]
        }

    test_cases = data.get("test_cases", [])

    if not isinstance(test_cases, list):

        return {
            "valid": False,
            "errors": [
                "'test_cases' must be a list"
            ]
        }

    for tc in test_cases:

        if not isinstance(tc, dict):

            errors.append(
                "Each test case must be a dictionary"
            )
            continue

        if not tc.get("id"):
            errors.append("Missing ID")

        if not tc.get("title"):
            errors.append(
                f"{tc.get('id', 'UNKNOWN')} missing title"
            )

        if not tc.get("steps"):
            errors.append(
                f"{tc.get('id', 'UNKNOWN')} missing steps"
            )

        if not tc.get("expected_result"):
            errors.append(
                f"{tc.get('id', 'UNKNOWN')} missing expected result"
            )

        if len(tc.get("steps", [])) == 0:
            errors.append(
                f"{tc.get('id', 'UNKNOWN')} has empty steps"
            )

    return {
        "valid": len(errors) == 0,
        "errors": errors
    }