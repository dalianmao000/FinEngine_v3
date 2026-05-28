import json
from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path

@dataclass
class TestCase:
    id: str
    question: str
    response: str
    reference: Optional[str] = None
    metadata: dict = None

class Dataset:
    def __init__(self):
        self.test_cases: List[TestCase] = []
        self._current_id = 0

    def load_json(self, file_path: str):
        path = Path(file_path)
        if not path.exists():
            self.test_cases = self._get_default_cases()
            return

        with open(path, "r") as f:
            data = json.load(f)
            for item in data.get("test_cases", []):
                self.add_case(
                    question=item["question"],
                    response=item["response"],
                    reference=item.get("reference"),
                )

    def add_case(
        self,
        question: str,
        response: str,
        reference: Optional[str] = None,
    ):
        self._current_id += 1
        self.test_cases.append(TestCase(
            id=f"case_{self._current_id}",
            question=question,
            response=response,
            reference=reference,
        ))

    def _get_default_cases(self) -> List[TestCase]:
        return [
            TestCase(
                id="case_1",
                question="What is your return policy?",
                response="We offer a 30-day return policy for all items in original condition.",
            ),
            TestCase(
                id="case_2",
                question="How can I reset my password?",
                response="Click the 'Forgot Password' link on the login page and follow the instructions sent to your email.",
            ),
        ]

    def to_list(self) -> List[dict]:
        return [
            {
                "id": tc.id,
                "question": tc.question,
                "response": tc.response,
                "reference": tc.reference,
            }
            for tc in self.test_cases
        ]