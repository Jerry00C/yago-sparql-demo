"""Build a fixed one-hop YAGO SPARQL query."""

import re


ALLOWED_PREDICATES = {
    "schema:birthPlace",
    "schema:birthDate",
    "schema:deathPlace",
    "schema:director",
    "schema:author",
}

SPARQL_TEMPLATE = """PREFIX yago: <http://yago-knowledge.org/resource/>
PREFIX schema: <http://schema.org/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?answer ?answerLabel
WHERE {{
  yago:{entity_id} {predicate} ?answer .

  OPTIONAL {{
    ?answer rdfs:label ?answerLabel .
    FILTER(LANG(?answerLabel) = "en")
  }}
}}
LIMIT 10"""


def build_sparql(entity_id: str, predicate: str) -> str:
    """Insert validated LLM fields into the fixed query template."""

    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_-]*", entity_id):
        raise ValueError("entity_id contains characters unsafe for a SPARQL prefix name")
    if predicate not in ALLOWED_PREDICATES:
        raise ValueError(f"unsupported predicate: {predicate}")

    return SPARQL_TEMPLATE.format(entity_id=entity_id, predicate=predicate)
