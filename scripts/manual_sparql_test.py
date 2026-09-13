"""Generate a SPARQL query from a manually written extraction."""

import json

from core.sparql_builder import build_sparql
from core.yago_client import execute_sparql, extract_answers


# Example of the structured information normally returned by the LLM.
extraction = {
    "entity_name": "Marie Curie",
    "entity_id": "Marie_Curie",
    "relationship": "birth date",
    "predicate": "schema:birthDate",
    "question_type": "date",
}

sparql_query = build_sparql(
    entity_id=extraction["entity_id"],
    predicate=extraction["predicate"],
)

print("Manual extraction:")
print(extraction)
print("\nGenerated SPARQL query:")
print(sparql_query)

yago_result = execute_sparql(sparql_query)
print("\nRaw YAGO response:")
print(json.dumps(yago_result, indent=2))

print("\nAnswers:")
for answer in extract_answers(yago_result):
    print(f"- {answer}")
