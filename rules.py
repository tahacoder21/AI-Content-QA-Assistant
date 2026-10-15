def calculate_overall_score(evaluations):

    total_score = sum(
        item["score"]
        for item in evaluations
    )

    max_score = len(evaluations) * 5

    percentage = round(
        (total_score / max_score) * 100,
        2
    )

    return total_score, max_score, percentage


def make_decision(percentage, evaluations):

    severities = [
        item["severity"]
        for item in evaluations
    ]

    # Critical issues always require rejection
    if "Critical" in severities:
        return "REJECT"

    # Very low overall quality
    if percentage < 50:
        return "REJECT"

    # Major safety issues require rejection
    for item in evaluations:

        if (
            item["criterion"] == "Safety"
            and item["severity"] == "Major"
        ):
            return "REJECT"

    # Other major issues require revision
    if "Major" in severities:
        return "REVISE"

    # Moderate overall quality
    if percentage < 80:
        return "REVISE"

    # High quality with no major/critical issues
    return "PUBLISH"


def get_overall_severity(evaluations):

    severities = [
        item["severity"]
        for item in evaluations
    ]

    if "Critical" in severities:
        return "Critical"

    if "Major" in severities:
        return "Major"

    if "Moderate" in severities:
        return "Moderate"

    return "Minor"


def get_top_issues(evaluations):

    issues = []

    for item in evaluations:

        if item["severity"] in ["Major", "Critical"]:

            issues.append({
                "criterion": item["criterion"],
                "issue": item["issue"],
                "severity": item["severity"],
                "recommendation": item["recommendation"]
            })

    return issues