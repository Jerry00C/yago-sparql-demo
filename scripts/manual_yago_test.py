"""Manually test a known query against the public YAGO endpoint.

This script does not call the LLM and does not need an OpenAI API key.
"""

import json

from core.yago_client import YagoClientError, execute_sparql, extract_answers


SPARQL_QUERY = """PREFIX yago: <http://yago-knowledge.org/resource/>
PREFIX schema: <http://schema.org/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?answer ?answerLabel
WHERE {
  yago:Albert_Einstein schema:birthPlace ?answer .

  OPTIONAL {
    ?answer rdfs:label ?answerLabel .
    FILTER(LANG(?answerLabel) = "en")
  }
}
LIMIT 10"""

SPARQL_QUERY2 = """
PREFIX yago: <http://yago-knowledge.org/resource/>
PREFIX schema: <http://schema.org/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?answer ?answerLabel
WHERE {
  yago:Marie_Curie schema:birthDate ?answer .

  OPTIONAL {
    ?answer rdfs:label ?answerLabel .
    FILTER(LANG(?answerLabel) = "en")
  }
}
LIMIT 10
"""

def manual_yago_test(query):
    """Run a known query against the public YAGO endpoint."""
    

    print("Sending this query to YAGO:\n")
    print(query)

    try:
        result = execute_sparql(query)
    except YagoClientError as exc:
        print(f"\nYAGO request failed: {exc}")
        return

    print("\nRaw YAGO response:")
    print(json.dumps(result, indent=2))

    answers = extract_answers(result)
    print("\nAnswers:")
    if not answers:
        print("No results found.")
    for answer in answers:
        print(f"- {answer}")

if __name__ == "__main__":
    manual_yago_test(SPARQL_QUERY2)
