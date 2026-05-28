from app.harness.eval.judge import Judge
from app.harness.eval.evaluator import Evaluator
from app.harness.eval.dataset import Dataset, TestCase

def test_judge_scores_response():
    judge = Judge()
    score = judge.evaluate(
        question="What is 2+2?",
        response="4",
        reference="4",
    )
    assert score.overall >= 0 and score.overall <= 1

def test_dataset_loads_json():
    dataset = Dataset()
    dataset.load_json("tests/fixtures/eval_dataset.json")
    assert len(dataset.test_cases) > 0