"""Streamlit frontend for the natural-language-to-YAGO pipeline."""

import streamlit as st

from core.llm_parser import StructuredQuestion, parse_question
from core.sparql_builder import build_sparql
from core.yago_client import execute_sparql, extract_answers


def render_pipeline(user_question: str) -> None:
    """Run the pipeline and render every step inside the current container."""

    user_question = user_question.strip()
    if not user_question:
        st.error("Enter a question before running the pipeline.")
        return

    with st.status("Receiving question", expanded=True) as status:
        st.write(user_question)
        status.update(label="Question received", state="complete")

    with st.status("Extracting structured information", expanded=True) as status:
        try:
            extraction = parse_question(user_question)
        except Exception as exc:
            status.update(label="Extraction failed", state="error")
            st.error(f"{type(exc).__name__}: {exc}")
            return
        st.json(extraction.model_dump())
        status.update(label="Extraction complete", state="complete")

    with st.status("Validating extraction", expanded=True) as status:
        try:
            validated = StructuredQuestion.model_validate(extraction.model_dump())
        except Exception as exc:
            status.update(label="Validation failed", state="error")
            st.error(f"{type(exc).__name__}: {exc}")
            return
        st.success("Entity, predicate, relationship, and question type are valid.")
        st.json(validated.model_dump())
        status.update(label="Validation passed", state="complete")

    with st.status("Building SPARQL query", expanded=True) as status:
        try:
            sparql_query = build_sparql(validated.entity_id, validated.predicate)
        except Exception as exc:
            status.update(label="Query generation failed", state="error")
            st.error(f"{type(exc).__name__}: {exc}")
            return
        st.code(sparql_query, language="sparql")
        status.update(label="SPARQL query built", state="complete")

    with st.status("Querying YAGO", expanded=True) as status:
        try:
            yago_result = execute_sparql(sparql_query)
        except Exception as exc:
            status.update(label="YAGO request failed", state="error")
            st.error(f"{type(exc).__name__}: {exc}")
            return
        st.json(yago_result)
        status.update(label="YAGO response received", state="complete")

    with st.status("Extracting answers", expanded=True) as status:
        try:
            answers = extract_answers(yago_result)
        except Exception as exc:
            status.update(label="Answer extraction failed", state="error")
            st.error(f"{type(exc).__name__}: {exc}")
            return

        if answers:
            st.success("\n\n".join(f"**{answer}**" for answer in answers))
        else:
            st.warning("YAGO returned no answers for this query.")
        status.update(label="Pipeline complete", state="complete")


st.set_page_config(
    page_title="YAGO Question Answering",
    page_icon="🔎",
    layout="centered",
)

st.title("YAGO Question Answering")
st.caption(
    "Ask a supported factual question and inspect every stage from LLM "
    "extraction to the final YAGO answer."
)

with st.sidebar:
    st.header("Supported relationships")
    st.markdown(
        """
- Birth place
- Birth date
- Death place
- Director
- Author
"""
    )
    st.caption("The extractor uses gpt-5-mini. Queries are limited to 10 results.")

with st.form("question_form"):
    user_question = st.text_input(
        "Your question",
        value="Where was Albert Einstein born?",
        placeholder="For example: Who directed Inception?",
    )
    submitted = st.form_submit_button("Run pipeline", type="primary")

output_area = st.empty()

if submitted:
    output_area.empty()
    with output_area.container():
        render_pipeline(user_question)
