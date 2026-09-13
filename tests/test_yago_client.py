import unittest

import requests

from core.yago_client import (
    YAGO_ENDPOINT,
    YagoClientError,
    execute_sparql,
    extract_answers,
)


class FakeResponse:
    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error

    def raise_for_status(self):
        if self.error:
            raise self.error

    def json(self):
        return self.result


class FakeSession:
    def __init__(self, response):
        self.response = response
        self.call = None

    def post(self, *args, **kwargs):
        self.call = (args, kwargs)
        return self.response


class YagoClientTests(unittest.TestCase):
    def test_extracts_label_and_falls_back_to_raw_answer(self):
        result = {
            "results": {
                "bindings": [
                    {
                        "answer": {"type": "uri", "value": "resource/Ulm"},
                        "answerLabel": {"type": "literal", "value": "Ulm"},
                    },
                    {
                        "answer": {
                            "type": "literal",
                            "value": "1867-11-07",
                        }
                    },
                ]
            }
        }

        self.assertEqual(extract_answers(result), ["Ulm", "1867-11-07"])

    def test_extract_answers_removes_duplicates(self):
        result = {
            "results": {
                "bindings": [
                    {"answer": {"value": "Ulm"}},
                    {"answerLabel": {"value": "Ulm"}},
                ]
            }
        }

        self.assertEqual(extract_answers(result), ["Ulm"])

    def test_extract_answers_rejects_invalid_shape(self):
        with self.assertRaisesRegex(YagoClientError, "results.bindings"):
            extract_answers({"results": {}})

    def test_posts_query_and_returns_json(self):
        expected = {"head": {"vars": ["answer"]}, "results": {"bindings": []}}
        session = FakeSession(FakeResponse(expected))

        result = execute_sparql("SELECT * WHERE {} LIMIT 1", session=session)

        self.assertEqual(result, expected)
        args, kwargs = session.call
        self.assertEqual(args[0], YAGO_ENDPOINT)
        self.assertEqual(kwargs["data"]["query"], "SELECT * WHERE {} LIMIT 1")
        self.assertEqual(
            kwargs["headers"]["Accept"], "application/sparql-results+json"
        )
        self.assertEqual(kwargs["timeout"], 20)

    def test_wraps_http_errors(self):
        error = requests.HTTPError("503 Server Error")
        session = FakeSession(FakeResponse(error=error))

        with self.assertRaisesRegex(YagoClientError, "YAGO request failed"):
            execute_sparql("SELECT * WHERE {}", session=session)

    def test_rejects_empty_query(self):
        with self.assertRaises(ValueError):
            execute_sparql("   ")

    def test_rejects_non_object_json(self):
        session = FakeSession(FakeResponse([]))

        with self.assertRaisesRegex(YagoClientError, "unexpected JSON"):
            execute_sparql("SELECT * WHERE {}", session=session)


if __name__ == "__main__":
    unittest.main()
