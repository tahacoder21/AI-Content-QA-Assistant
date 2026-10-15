# AI Content QA Assistant

A rule-based quality-assurance tool that reviews written content across seven criteria and produces a score, severity assessment, publication decision, and recommended actions.

## Features

- Evaluates content across seven criteria:
  - Safety
  - Accuracy
  - Instruction Following
  - Hallucination Control
  - Evidence Quality
  - Tone
  - Grammar & Readability
- Scores each criterion from 1 to 5.
- Calculates an overall score out of 100.
- Identifies top issues and provides recommendations.
- Applies safety-first publication decisions:
  - **PUBLISH** when content meets the configured quality thresholds.
  - **REVISE** when content needs corrections or additional evidence.
  - **REJECT** when critical issues or defined serious safety concerns are detected.
- Includes unit tests, labeled-dataset evaluation, adversarial cases, and report examples.

## How the decision logic works

The decision rules prioritize safety over the aggregate score. For example, content can receive a high overall score and still be rejected when a Major Safety issue is detected. Unsupported factual claims can be sent for revision rather than being published automatically.

## Project structure

```text
ai-content-qa/
├── app.py
├── evaluator.py
├── rules.py
├── prompts.py
├── requirements.txt
├── README.md
├── test_qa.py
├── test_cases.py
├── evaluate_dataset.py
├── qa_report.py
└── adversarial_cases.py
```

## Setup

1. Open a terminal in the project directory.
2. Create and activate a virtual environment (recommended).
3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the application using the command appropriate to the app configured in `app.py`. If it is a Streamlit app, use:

   ```bash
   streamlit run app.py
   ```

## Testing

Run the unit tests:

```bash
python -m unittest discover -s . -p "test_qa.py" -v
```

Evaluate the labeled dataset:

```bash
python evaluate_dataset.py
```

Review the generated QA report examples:

```bash
python qa_report.py
```

Run adversarial test cases:

```bash
python adversarial_cases.py
```

## Current test results

Results from the current development test set:

- **Unit tests:** 10/10 passed.
- **Labeled dataset:** 22/22 expected labels matched (100% agreement on this dataset).
- **Report scenarios:** safe content returned `PUBLISH`; an unsupported factual claim returned `REVISE`; academic-dishonesty content returned `REJECT`.
- **Adversarial cases:** 12 cases were reviewed to check how the evaluator responds to safe, qualified, unsupported, and absolute claims.

These results describe performance on the current test cases only. They do **not** establish 100% real-world accuracy or prove that the tool catches every hallucination.

## Limitations

- The evaluator is primarily rule-based and detects predefined language patterns.
- It does not independently verify every factual claim against external sources.
- Pattern-based rules may miss unfamiliar wording or flag some claims that need human interpretation.
- The labeled dataset is small, and some criteria have very few examples. More varied, independently labeled examples are needed before making broad performance claims.
- Human review remains important, especially for factual claims and high-impact content.

## Future improvements

- Expand the labeled dataset with more examples for every criterion.
- Add more tests for paraphrased claims and false positives.
- Integrate reliable source retrieval or fact-checking for claims that need evidence.
- Track false-positive and false-negative rates by criterion.
- Improve the interface and exportable report format based on user feedback.

