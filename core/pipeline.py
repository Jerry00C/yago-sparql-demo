"""Run the complete natural-language-to-YAGO pipeline one step at a time."""

import json

from .llm_parser import StructuredQuestion, parse_question
from .sparql_builder import build_sparql
from .yago_client import execute_sparql, extract_answers


def print_heading(step: int, title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"STEP {step}: {title}")
    print("=" * 60)


def step_1_receive_question(question: str) -> str:
    print_heading(1, "Receive question")
    print(question)
    return question


def step_2_extract_information(question: str) -> StructuredQuestion:
    print_heading(2, "Extract structured information with the LLM")
    extraction = parse_question(question)
    print(extraction.model_dump_json(indent=2))
    return extraction


def step_3_validate_extraction(
    extraction: StructuredQuestion,
) -> StructuredQuestion:
    print_heading(3, "Validate extraction")
    validated = StructuredQuestion.model_validate(extraction.model_dump())
    print("Validation passed.")
    print(validated.model_dump_json(indent=2))
    return validated


def step_4_build_query(extraction: StructuredQuestion) -> str:
    print_heading(4, "Build SPARQL query")
    query = build_sparql(extraction.entity_id, extraction.predicate)
    print(query)
    return query


def step_5_execute_query(query: str) -> dict:
    print_heading(5, "Execute query against YAGO")
    result = execute_sparql(query)
    print(json.dumps(result, indent=2))
    return result


def step_6_extract_answers(result: dict) -> list:
    print_heading(6, "Extract answers from YAGO response")
    answers = extract_answers(result)
    if answers:
        for answer in answers:
            print(f"- {answer}")
    else:
        print("No answers found.")
    return answers


def run_pipeline(user_question: str) -> None:
    """Run each pipeline step sequentially and print every output."""

    current_step = 1
    try:
        question = step_1_receive_question(user_question)

        current_step = 2
        extraction = step_2_extract_information(question)

        current_step = 3
        validated_extraction = step_3_validate_extraction(extraction)

        current_step = 4
        query = step_4_build_query(validated_extraction)

        current_step = 5
        result = step_5_execute_query(query)

        current_step = 6
        step_6_extract_answers(result)
    except Exception as exc:
        print_heading(current_step, "Error")
        print(f"{type(exc).__name__}: {exc}")


if __name__ == "__main__":
    user_question = "Marie Curie was born in Warsaw and later died in Passy; without returning either location, what calendar value should the system retrieve for the beginning of her life?"
    run_pipeline(user_question)
