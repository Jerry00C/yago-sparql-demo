import unittest

from core.sparql_builder import build_sparql


class SparqlBuilderTests(unittest.TestCase):
    def test_inserts_llm_fields(self):
        query = build_sparql("Marie_Curie", "schema:birthDate")

        self.assertIn("yago:Marie_Curie schema:birthDate ?answer .", query)
        self.assertIn('FILTER(LANG(?answerLabel) = "en")', query)
        self.assertTrue(query.endswith("LIMIT 10"))

    def test_rejects_unknown_predicate(self):
        with self.assertRaises(ValueError):
            build_sparql("Marie_Curie", "schema:knows")

    def test_rejects_unsafe_entity_id(self):
        with self.assertRaises(ValueError):
            build_sparql("Marie_Curie; DROP ALL", "schema:birthDate")


if __name__ == "__main__":
    unittest.main()
