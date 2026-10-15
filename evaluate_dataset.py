from evaluator import rule_based_evaluate
from test_cases import test_cases


CRITERIA = [
    "Safety",
    "Accuracy",
    "Instruction Following",
    "Hallucination Control",
    "Evidence Quality",
    "Tone",
    "Grammar & Readability"
]


def evaluate_criterion(case, criterion):

    evaluations = rule_based_evaluate(
        case["prompt"],
        case["response"]
    )

    result = next(
        item
        for item in evaluations
        if item["criterion"] == criterion
    )

    return result


def run_dataset():

    print("\nAI CONTENT QA - MULTI-CRITERION DATASET")
    print("=" * 60)

    results = []

    for case in test_cases:

        print(f"\n{case['name']}")
        print("-" * 40)

        expected_values = case.get("expected", {})

        for criterion, expected in expected_values.items():

            result = evaluate_criterion(
                case,
                criterion
            )

            predicted = result["severity"]

            if predicted == expected:
                status = "PASS"
            else:
                status = "FAIL"

            results.append({
                "case": case["name"],
                "criterion": criterion,
                "expected": expected,
                "predicted": predicted,
                "status": status
            })

            print(f"Criterion: {criterion}")
            print(f"Expected:  {expected}")
            print(f"Predicted: {predicted}")
            print(f"Result:    {status}")

    return results


def calculate_results(results):

    total = len(results)

    correct = sum(
        1
        for result in results
        if result["status"] == "PASS"
    )

    accuracy = (
        correct / total * 100
        if total > 0
        else 0
    )

    return correct, total, accuracy


def calculate_criterion_accuracy(results):

    criterion_results = {}

    for criterion in CRITERIA:

        relevant = [
            result
            for result in results
            if result["criterion"] == criterion
        ]

        if not relevant:
            continue

        correct = sum(
            1
            for result in relevant
            if result["status"] == "PASS"
        )

        total = len(relevant)

        accuracy = correct / total * 100

        criterion_results[criterion] = {
            "correct": correct,
            "total": total,
            "accuracy": accuracy
        }

    return criterion_results


def print_summary(results):

    correct, total, accuracy = calculate_results(
        results
    )

    print("\n" + "=" * 60)
    print("OVERALL DATASET RESULTS")
    print("=" * 60)

    print(
        f"Correct predictions: {correct}/{total}"
    )

    print(
        f"Overall accuracy: {accuracy:.2f}%"
    )

    print("\n" + "=" * 60)
    print("ACCURACY BY CRITERION")
    print("=" * 60)

    criterion_results = calculate_criterion_accuracy(
        results
    )

    for criterion, data in criterion_results.items():

        print(
            f"{criterion}: "
            f"{data['correct']}/{data['total']} "
            f"({data['accuracy']:.2f}%)"
        )

    failures = [
        result
        for result in results
        if result["status"] == "FAIL"
    ]

    print("\n" + "=" * 60)
    print("FAILED CASES")
    print("=" * 60)

    if not failures:

        print("No failures.")

    else:

        for failure in failures:

            print(
                f"\nCase: {failure['case']}"
            )

            print(
                f"Criterion: {failure['criterion']}"
            )

            print(
                f"Expected: {failure['expected']}"
            )

            print(
                f"Predicted: {failure['predicted']}"
            )


if __name__ == "__main__":

    results = run_dataset()

    print_summary(results)
    