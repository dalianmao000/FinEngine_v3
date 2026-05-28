from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from app.harness.eval import Judge, Evaluator, Dataset

router = APIRouter()
judge = Judge()
evaluator = Evaluator(judge)
dataset = Dataset()

class EvalRunRequest(BaseModel):
    dataset_id: str
    model_id: str
    prompt_version: str = "v1"

class EvalResultResponse(BaseModel):
    average_scores: dict
    total_cases: int
    passed_cases: int

@router.post("/eval/run")
async def run_eval(request: EvalRunRequest):
    test_cases = dataset.to_list()
    report = evaluator.run_eval(test_cases, request.model_id, request.prompt_version)

    return EvalResultResponse(
        average_scores=report.average_scores,
        total_cases=report.total_cases,
        passed_cases=report.passed_cases,
    )

@router.get("/eval/results")
async def get_results():
    return {"results": []}

@router.post("/eval/dataset")
async def upload_dataset(cases: List[dict]):
    for case in cases:
        dataset.add_case(
            question=case["question"],
            response=case["response"],
            reference=case.get("reference"),
        )
    return {"status": "uploaded", "count": len(cases)}

@router.get("/eval/dataset")
async def list_dataset():
    return {"cases": dataset.to_list()}