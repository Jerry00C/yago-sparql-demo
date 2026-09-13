"""Execute SPARQL queries against YAGO's public endpoint."""

from typing import Any, Dict, List, Optional

import requests


YAGO_ENDPOINT = "https://yago-knowledge.org/sparql/qlever"
DEFAULT_TIMEOUT_SECONDS = 20


class YagoClientError(RuntimeError):
    """Raised when YAGO cannot return a usable SPARQL JSON response."""


def extract_answers(result: Dict[str, Any]) -> List[str]:
    """Extract answer values from a YAGO SPARQL JSON response.

    Human-readable ``answerLabel`` values are preferred. If a row has no label,
    the raw ``answer`` value is returned instead. Duplicate values are removed
    while preserving their original order.
    """

    try:
        bindings = result["results"]["bindings"]
    except (KeyError, TypeError) as exc:
        raise YagoClientError("YAGO response has no results.bindings list") from exc

    if not isinstance(bindings, list):
        raise YagoClientError("YAGO response results.bindings is not a list")

    answers = []
    for binding in bindings:
        if not isinstance(binding, dict):
            continue

        label = binding.get("answerLabel")
        answer = binding.get("answer")
        selected = label if isinstance(label, dict) and label.get("value") else answer

        if isinstance(selected, dict):
            value = selected.get("value")
            if isinstance(value, str) and value not in answers:
                answers.append(value)

    return answers


def execute_sparql(
    query: str,
    *,
    endpoint: str = YAGO_ENDPOINT,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
    session: Optional[Any] = None,
) -> Dict[str, Any]:
    """Send ``query`` to YAGO and return its decoded JSON response."""

    if not query.strip():
        raise ValueError("SPARQL query must not be empty")

    http = session or requests
    try:
        response = http.post(
            endpoint,
            data={"query": query},
            headers={"Accept": "application/sparql-results+json"},
            timeout=timeout,
        )
        response.raise_for_status()
        result = response.json()
    except requests.RequestException as exc:
        raise YagoClientError(f"YAGO request failed: {exc}") from exc
    except ValueError as exc:
        raise YagoClientError("YAGO returned a response that was not valid JSON") from exc

    if not isinstance(result, dict):
        raise YagoClientError("YAGO returned an unexpected JSON response")

    return result
