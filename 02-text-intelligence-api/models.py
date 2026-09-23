from pydantic import BaseModel, Field 
from typing import Literal

class ProcessRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Texte à traiter")
    task: Literal["summarize", "translate", "classify"] 
    target_language: str | None = None
    

class ProcessResponse(BaseModel):
    task: str
    result:str
    original_lengt : int 
    