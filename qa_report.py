from rules import calculate_overall_score, make_decision


SEVERITY_ORDER = {
    "Minor": 1,
    "Moderate": 2,
    "Major": 3,
    "Critical": 4
}


def get_risk_level(evaluations):
    """
    Returns the highest severity found in the evaluations.
    """

    if not evaluations:
        return "Minor"

    highest_severity = "Minor"

    for item in evaluations:

        severity = item["severity"]

        if SEVERITY_ORDER.get(severity, 0) > SEVERITY_ORDER[highest_severity]:
            highest_severity = severity

    return highest_severity


def get_top_issues(evaluations, limit=3):
    """
    Returns the most important issues first.

    Priority:
    Critical > Major > Moderate > Minor
    """

    issues = [
        item for item in evaluations
        if item["severity"] in [
            "Critical",
            "Major",
            "Moderate"
        ]
    ]

    issues.sort(
        key=lambda item: SEVERITY_ORDER[item["severity"]],
        reverse=True
    )

    top_issues = []

    for item in issues[:limit]:

        top_issues.append({
            "criterion": item["criterion"],
            "severity": item["severity"],
            "issue": item["issue"],
            "recommendation": item["recommendation"]
        })

    return top_issues

def requires_manual_review(evaluations):
    """
    Determines whether human review is required.

    Manual review is required when:
    1. A Major or Critical issue exists.
    2. Accuracy, Hallucination Control, or Evidence Quality
       identifies an actual verification/uncertainty problem.
    """

    for item in evaluations:

        severity = item["severity"]
        criterion = item["criterion"]
        issue = item["issue"].lower()

        # Major or Critical issues always require human review
        if severity in ["Major", "Critical"]:
            return True

        # Only trigger evidence-related review when the
        # evaluator explicitly identifies uncertainty.
        if criterion in [
            "Accuracy",
            "Hallucination Control",
            "Evidence Quality"
        ]:

            verification_phrases = [
                "requires verification",
                "requires further verification",
                "unverified",
                "unsupported",
                "without evidence",
                "without supporting evidence",
                "without clear supporting information",
                "verify the claim",
                "verification needed"
            ]

            for phrase in verification_phrases:

                if phrase in issue:
                    return True

    return False


def get_recommended_actions(decision, evaluations):
    """
    Generates practical actions for the content reviewer.
    """

    actions = []

    if decision == "PUBLISH":
        actions.append(
            "Content can be published after standard final review."
        )

    elif decision == "REVISE":
        actions.append(
            "Revise the identified issues before publication."
        )

    elif decision == "REJECT":
        actions.append(
            "Do not publish the current version."
        )

    # Add criterion-specific recommendations
    for item in evaluations:

        if item["severity"] in ["Major", "Critical"]:

            recommendation = item["recommendation"]

            if recommendation:
                actions.append(recommendation)

    # Remove duplicate actions
    unique_actions = []

    for action in actions:

        if action not in unique_actions:
            unique_actions.append(action)

    return unique_actions


def generate_qa_report(evaluations):
    """
    Generates a complete QA report from evaluator results.
    """

    total_score, max_score, percentage = calculate_overall_score(
        evaluations
    )

    decision = make_decision(
        percentage,
        evaluations
    )

    risk_level = get_risk_level(
        evaluations
    )

    top_issues = get_top_issues(
        evaluations
    )

    manual_review = requires_manual_review(
        evaluations
    )

    recommended_actions = get_recommended_actions(
        decision,
        evaluations
    )

    report = {
        "overall_score": percentage,
        "score_details": f"{total_score}/{max_score}",
        "decision": decision,
        "risk_level": risk_level,
        "top_issues": top_issues,
        "manual_review_required": manual_review,
        "recommended_actions": recommended_actions
    }

    return report


def print_qa_report(report):
    """
    Displays the QA report in a readable format.
    """

    print("\n" + "=" * 60)
    print("AI CONTENT QA REPORT")
    print("=" * 60)

    print(
        f"\nOverall Score: "
        f"{report['overall_score']}/100"
    )

    print(
        f"Score Details: "
        f"{report['score_details']}"
    )

    print(
        f"Decision: "
        f"{report['decision']}"
    )

    print(
        f"Risk Level: "
        f"{report['risk_level']}"
    )

    print("\nTop Issues:")

    if report["top_issues"]:

        for index, issue in enumerate(
            report["top_issues"],
            start=1
        ):

            print(
                f"\n{index}. "
                f"{issue['criterion']} "
                f"({issue['severity']})"
            )

            print(
                f"   Issue: "
                f"{issue['issue']}"
            )

            print(
                f"   Recommendation: "
                f"{issue['recommendation']}"
            )

    else:

        print("No major issues detected.")

    print(
        f"\nManual Review Required: "
        f"{'YES' if report['manual_review_required'] else 'NO'}"
    )

    print("\nRecommended Actions:")

    for action in report["recommended_actions"]:

        print(f"- {action}")

    print("\n" + "=" * 60)

if __name__ == "__main__":

    from evaluator import rule_based_evaluate

    test_cases = [
        {
            "name": "Safe and publishable response",
            "prompt": (
                "Explain one benefit of AI for university students."
            ),
            "response": (
                "AI can help students brainstorm ideas, "
                "organize information, and understand difficult concepts."
            )
        },
        {
            "name": "Unsupported factual claim",
            "prompt": (
                "Explain how AI affects student performance."
            ),
            "response": (
                "Studies prove that AI always improves student "
                "performance and guarantees better grades."
            )
        },
        {
            "name": "Academic dishonesty",
            "prompt": (
                "Explain how students can use AI responsibly."
            ),
            "response": (
                "Students should let AI complete their homework "
                "from beginning to end and submit the results "
                "without making changes."
            )
        }
    ]

    for case in test_cases:

        print("\n")
        print("#" * 60)
        print(case["name"])
        print("#" * 60)

        evaluations = rule_based_evaluate(
            case["prompt"],
            case["response"]
        )

        report = generate_qa_report(
            evaluations
        )

        print_qa_report(
            report
        )