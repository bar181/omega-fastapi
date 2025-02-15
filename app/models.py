from pydantic import BaseModel
from typing import Optional

class OmegaRequest(BaseModel):
    omega: str
    model: Optional[str] = None

class OmegaResponse(BaseModel):
    result: str

class HumanToOmegaRequest(BaseModel):
    human_text: str

class OmegaValidationRequest(BaseModel):
    omega: str

class OmegaCorrectionRequest(BaseModel):
    omega: str
    attempt: Optional[int] = 1

class OmegaToHumanRequest(BaseModel):
    omega: str

class ReasoningRequest(BaseModel):
    omega: str

class OmegaReflectionRequest(BaseModel):
    omega: str

class OmegaImproveRequest(BaseModel):
    omega: str
    feedback: Optional[str] = None
    score: Optional[int] = None
