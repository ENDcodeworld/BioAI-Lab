"""
Protein Prediction Router
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class ProteinPredictRequest(BaseModel):
    sequence: str
    model: str = "esmfold"
    return_confidence: bool = True


class ProteinPredictResponse(BaseModel):
    job_id: str
    status: str
    result: Optional[dict] = None


@router.post("/predict", response_model=ProteinPredictResponse)
async def predict_protein(request: ProteinPredictRequest):
    """
    Submit protein structure prediction job.
    """
    # TODO: Implement prediction
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.get("/predict/{job_id}", response_model=ProteinPredictResponse)
async def get_prediction(job_id: str):
    """
    Get prediction job status and result.
    """
    # TODO: Implement
    raise HTTPException(status_code=501, detail="Not implemented yet")
