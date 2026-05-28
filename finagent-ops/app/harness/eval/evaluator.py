from dataclasses import dataclass
from typing import List
from datetime import datetime

from app.harness.eval.judge import Judge, JudgeScore

@dataclass
class EvalReport:
    dataset_id: str
    model_id: str
    prompt_version: str
    average_scores: dict
    total_cases: int
    passed_cases: int
    tokens_used: int
    evaluated_at: str

class Evaluator:
    def __init__(self, judge: Judge):
        self.judge = judge

    def run_eval(
        self,
        test_cases: List[dict],
        model_id: str,
        prompt_version: str = "v1",
    ) -> EvalReport:
        scores_list = []
        tokens_used = 0
        passed = 0

        for case in test_cases:
            score = self.judge.evaluate(
                question=case["question"],
                response=case["response"],
                reference=case.get("reference"),
            )
            scores_list.append(score)
            tokens_used += len(case["question"].split()) * 2
            if score.overall >= 0.7:
                passed += 1

        avg_accuracy = sum(s.accuracy for s in scores_list) / len(scores_list)
        avg_relevance = sum(s.relevance for s in scores_list) / len(scores_list)
        avg_safety = sum(s.safety for s in scores_list) / len(scores_list)
        avg_hallucination = sum(s.hallucination for s in scores_list) / len(scores_list)
        avg_overall = sum(s.overall for s in scores_list) / len(scores_list)

        return EvalReport(
            dataset_id="dataset_001",
            model_id=model_id,
            prompt_version=prompt_version,
            average_scores={
                "accuracy": avg_accuracy,
                "relevance": avg_relevance,
                "safety": avg_safety,
                "hallucination": avg_hallucination,
                "overall": avg_overall,
            },
            total_cases=len(test_cases),
            passed_cases=passed,
            tokens_used=tokens_used,
            evaluated_at=datetime.utcnow().isoformat(),
        )