import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from core.llm_parser import StructuredQuestion
from core.pipeline import run_pipeline


class PipelineTests(unittest.TestCase):
    def test_runs_and_prints_every_step_in_order(self):
        extraction = StructuredQuestion(
            entity_name="Albert Einstein",
            entity_id="Albert_Einstein",
            relationship="birth place",
            predicate="schema:birthPlace",
            question_type="place",
        )
        yago_result = {"results": {"bindings": []}}

        output = io.StringIO()
        with patch("core.pipeline.parse_question", return_value=extraction), patch(
            "core.pipeline.execute_sparql", return_value=yago_result
        ), redirect_stdout(output):
            run_pipeline("Where was Albert Einstein born?")

        printed = output.getvalue()
        positions = [printed.index(f"STEP {step}:") for step in range(1, 7)]
        self.assertEqual(positions, sorted(positions))
        self.assertIn('"entity_id": "Albert_Einstein"', printed)
        self.assertIn("yago:Albert_Einstein schema:birthPlace ?answer", printed)
        self.assertIn('"bindings": []', printed)
        self.assertIn("No answers found.", printed)


if __name__ == "__main__":
    unittest.main()
