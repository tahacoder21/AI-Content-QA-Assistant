import streamlit as st

from evaluator import (
    rule_based_evaluate,
    parse_llm_evaluation
)

from prompts import build_structured_evaluation_prompt

from rules import (
    calculate_overall_score,
    make_decision,
    get_overall_severity,
    get_top_issues
)


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="AI Content QA Assistant",
    page_icon="🤖",
    layout="wide"
)


# ==================================================
# FUNCTION 1: DISPLAY QA REPORT
# ==================================================

def display_report(evaluations):

    # Calculate the overall score
    total, maximum, percentage = calculate_overall_score(
        evaluations
    )

    # Determine the final decision
    decision = make_decision(
        percentage,
        evaluations
    )

    # Determine the overall severity
    overall_severity = get_overall_severity(
        evaluations
    )

    # Identify the highest-priority issues
    top_issues = get_top_issues(
        evaluations
    )

    st.divider()
    st.header("QA Report")

    # ---------------- SUMMARY METRICS ----------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Score",
            f"{total}/{maximum}"
        )

    with col2:
        st.metric(
            "Overall Score",
            f"{percentage}/100"
        )

    with col3:
        st.metric(
            "Decision",
            decision
        )

    with col4:
        st.metric(
            "Overall Severity",
            overall_severity
        )

    # ---------------- DECISION MESSAGE ----------------

    if decision == "PUBLISH":

        st.success(
            "✅ PUBLISH — No blocking issues were identified "
            "by the selected evaluation method."
        )

    elif decision == "REVISE":

        st.warning(
            "⚠️ REVISE — The content requires improvements "
            "before publication."
        )

    else:

        st.error(
            "🚫 REJECT — The evaluation identified serious "
            "quality or safety concerns."
        )

    # ---------------- QUALITY SCORE ----------------

    st.subheader("Quality Score")

    st.progress(
        percentage / 100
    )

    st.caption(
        f"Overall quality score: {percentage}/100"
    )

    # ---------------- CRITERIA OVERVIEW ----------------

    st.subheader("Criteria Overview")

    severity_icons = {
        "Minor": "🟢",
        "Moderate": "🟡",
        "Major": "🟠",
        "Critical": "🔴"
    }

    # Display three criteria per row
    for start in range(0, len(evaluations), 3):

        row_items = evaluations[start:start + 3]

        columns = st.columns(3)

        for column, item in zip(columns, row_items):

            with column:

                icon = severity_icons.get(
                    item["severity"],
                    "⚪"
                )

                st.markdown(
                    f"**{item['criterion']}**"
                )

                st.metric(
                    "Score",
                    f"{item['score']}/5"
                )

                st.write(
                    f"{icon} {item['severity']}"
                )

                st.progress(
                    item["score"] / 5
                )

    # ---------------- TOP ISSUES ----------------

    st.subheader("Top Issues")

    if top_issues:

        for index, item in enumerate(
            top_issues,
            start=1
        ):

            st.write(
                f'{index}. **{item["criterion"]}** — '
                f'{item["issue"]} '
                f'({item["severity"]})'
            )

    else:

        st.success(
            "No significant issues identified "
            "by the selected evaluation method."
        )

    # ---------------- TOP RECOMMENDATIONS ----------------

    st.subheader("Top Recommendations")

    if top_issues:

        for index, item in enumerate(
            top_issues,
            start=1
        ):

            st.write(
                f'{index}. {item["recommendation"]}'
            )

    else:

        st.write(
            "No major recommendations required."
        )

    # ---------------- DETAILED EVALUATION ----------------

    st.subheader("Detailed Evaluation")

    for item in evaluations:

        with st.expander(
            f'{item["criterion"]} — {item["score"]}/5'
        ):

            st.write(
                "**Reason:**",
                item["reason"]
            )

            st.write(
                "**Issue:**",
                item["issue"]
            )

            st.write(
                "**Severity:**",
                item["severity"]
            )

            st.write(
                "**Recommendation:**",
                item["recommendation"]
            )

    st.info(
        "This report is an automated assessment. "
        "Important factual claims, safety concerns, "
        "and publication decisions should be reviewed manually."
    )


# ==================================================
# FUNCTION 2: COMPARE EVALUATORS
# ==================================================

def compare_evaluators(
    original_prompt,
    ai_response,
    llm_evaluations
):

    st.divider()

    st.header("Evaluation Comparison")

    # ---------------- RULE-BASED RESULTS ----------------

    rule_results = rule_based_evaluate(
        original_prompt,
        ai_response
    )

    _, _, rule_percentage = calculate_overall_score(
        rule_results
    )

    rule_decision = make_decision(
        rule_percentage,
        rule_results
    )

    # ---------------- LLM RESULTS ----------------

    _, _, llm_percentage = calculate_overall_score(
        llm_evaluations
    )

    llm_decision = make_decision(
        llm_percentage,
        llm_evaluations
    )

    # ---------------- COMPARISON METRICS ----------------

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("Rule-Based Evaluation")

        st.metric(
            "Overall Score",
            f"{rule_percentage}/100"
        )

        st.write(
            f"**Decision:** {rule_decision}"
        )

    with col2:

        st.subheader("LLM-Assisted Evaluation")

        st.metric(
            "Overall Score",
            f"{llm_percentage}/100"
        )

        st.write(
            f"**Decision:** {llm_decision}"
        )

    # ---------------- CRITERIA COMPARISON ----------------

    st.subheader("Criteria Comparison")

    # Match results using criterion names
    rule_lookup = {
        item["criterion"]: item
        for item in rule_results
    }

    comparison = []

    for llm_item in llm_evaluations:

        criterion = llm_item["criterion"]

        rule_item = rule_lookup[criterion]

        difference = (
            llm_item["score"] - rule_item["score"]
        )

        comparison.append({
            "Criterion": criterion,
            "Rule-Based": rule_item["score"],
            "LLM": llm_item["score"],
            "Difference": difference,
            "Rule Severity": rule_item["severity"],
            "LLM Severity": llm_item["severity"]
        })

    # Display the table ONLY ONCE
    st.table(comparison)

    st.caption(
        "Difference = LLM score minus Rule-Based score. "
        "A negative value means the LLM assigned a lower score."
    )

    # ---------------- AGREEMENT CHECK ----------------

    st.subheader("Evaluation Agreement")

    if rule_decision != llm_decision:

        st.warning(
            "⚠️ The two evaluation methods disagree "
            "on the final decision. Manual review is recommended."
        )

    else:

        st.success(
            "Both evaluation methods produced "
            "the same final decision."
        )

    # ---------------- SCORE DISAGREEMENTS ----------------

    disagreements = [
        item
        for item in comparison
        if item["Difference"] != 0
    ]

    if disagreements:

        st.write(
            f"**Score disagreements detected:** "
            f"{len(disagreements)} of 7 criteria"
        )

        for item in disagreements:

            st.write(
                f'- **{item["Criterion"]}:** '
                f'Rule-Based {item["Rule-Based"]}/5 '
                f'vs LLM {item["LLM"]}/5 '
                f'(Difference: {item["Difference"]})'
            )

    else:

        st.success(
            "Both evaluators assigned identical scores "
            "to all seven criteria."
        )

    st.info(
        "Agreement does not guarantee accuracy. "
        "Investigate disagreements rather than automatically "
        "accepting either evaluator."
    )


# ==================================================
# MAIN APPLICATION
# ==================================================

st.title("🤖 AI Content QA Assistant")

st.write(
    "Evaluate AI-generated content using rule-based "
    "analysis or LLM-assisted evaluation."
)


# ---------------- EVALUATION MODE ----------------

evaluation_mode = st.radio(
    "Select Evaluation Mode",
    [
        "Rule-Based",
        "LLM-Assisted (Manual)"
    ],
    horizontal=True
)


# ---------------- USER INPUT ----------------

st.subheader("Content to Evaluate")

original_prompt = st.text_area(
    "Original Prompt",
    placeholder="Enter the original user prompt...",
    height=150
)

ai_response = st.text_area(
    "AI Response",
    placeholder="Paste the AI-generated response...",
    height=200
)


# ==================================================
# MODE 1: RULE-BASED EVALUATION
# ==================================================

if evaluation_mode == "Rule-Based":

    st.info(
        "This mode uses Python rules and pattern detection. "
        "It does not independently verify factual claims."
    )

    if st.button("Evaluate Response"):

        if (
            not original_prompt.strip()
            or not ai_response.strip()
        ):

            st.warning(
                "Please enter both the original prompt "
                "and AI response."
            )

        else:

            # Run rule-based evaluation
            evaluations = rule_based_evaluate(
                original_prompt,
                ai_response
            )

            # Display the report
            display_report(
                evaluations
            )


# ==================================================
# MODE 2: LLM-ASSISTED EVALUATION
# ==================================================

else:

    st.subheader("LLM Evaluation Prompt")

    st.write(
        "Copy the generated evaluation prompt into ChatGPT. "
        "Then paste the resulting JSON below."
    )

    # ---------------- GENERATE PROMPT ----------------

    if (
        original_prompt.strip()
        and ai_response.strip()
    ):

        generated_prompt = build_structured_evaluation_prompt(
            original_prompt,
            ai_response
        )

        st.code(
            generated_prompt,
            language="text"
        )

    else:

        st.info(
            "Enter both inputs to generate "
            "your evaluation prompt."
        )

    # ---------------- LLM JSON INPUT ----------------

    raw_json = st.text_area(
        "Paste LLM Evaluation JSON",
        placeholder="Paste the complete JSON response here...",
        height=250
    )

    # ---------------- PROCESS LLM RESPONSE ----------------

    if st.button("Generate QA Report"):

        if (
            not original_prompt.strip()
            or not ai_response.strip()
        ):

            st.warning(
                "Please provide the original prompt "
                "and AI response."
            )

        elif not raw_json.strip():

            st.warning(
                "Please paste the LLM evaluation JSON."
            )

        else:

            try:

                # Parse and validate the JSON
                evaluations = parse_llm_evaluation(
                    raw_json
                )

                st.success(
                    "JSON validation successful!"
                )

                # Compare both methods
                compare_evaluators(
                    original_prompt,
                    ai_response,
                    evaluations
                )

                # Display the full LLM report
                st.header(
                    "LLM Evaluation Results"
                )

                display_report(
                    evaluations
                )

            except ValueError as error:

                st.error(
                    f"JSON Validation Error: {error}"
                )