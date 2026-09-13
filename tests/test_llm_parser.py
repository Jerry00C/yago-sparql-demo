import unittest
from types import SimpleNamespace

from pydantic import ValidationError

from core.llm_parser import (
    ExtractionEnvelope,
    LLMResponseError,
    MODEL,
    StructuredQuestion,
    UnsupportedQuestionError,
    parse_question,
)


class FakeResponses:
    def __init__(self, output_parsed):
        self.output_parsed = output_parsed
        self.call = None

    def parse(self, **kwargs):
        self.call = kwargs
        return SimpleNamespace(output_parsed=self.output_parsed)


class FakeClient:
    def __init__(self, output_parsed):
        self.responses = FakeResponses(output_parsed)


class LlmParserTests(unittest.TestCase):
    def test_extracts_supported_question(self):
        expected = StructuredQuestion(
            entity_name="Inception",
            entity_id="Inception",
            relationship="director",
            predicate="schema:director",
            question_type="person",
        )
        client = FakeClient(
            ExtractionEnvelope(supported=True, extraction=expected, error=None)
        )

        actual = parse_question("Who directed Inception?", client=client)

        self.assertEqual(actual, expected)
        self.assertEqual(client.responses.call["model"], MODEL)

    def test_rejects_mismatched_relationship_and_predicate(self):
        with self.assertRaises(ValidationError):
            StructuredQuestion(
                entity_name="Inception",
                entity_id="Inception",
                relationship="director",
                predicate="schema:author",
                question_type="person",
            )

    def test_reports_unsupported_question(self):
        client = FakeClient(
            ExtractionEnvelope(
                supported=False,
                extraction=None,
                error="relationship is not supported",
            )
        )

        with self.assertRaises(UnsupportedQuestionError):
            parse_question("What is the population of Paris?", client=client)

    def test_reports_missing_parsed_output(self):
        with self.assertRaises(LLMResponseError):
            parse_question("Who directed Inception?", client=FakeClient(None))


if __name__ == "__main__":
    unittest.main()
