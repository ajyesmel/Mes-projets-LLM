"""Modèles Pydantic pour les sorties structurées (réutilisés depuis S3)."""
from typing import Literal
from pydantic import BaseModel


class TaskExtraction(BaseModel):
    titre: str
    priorite: Literal["basse", "normale", "haute"]
    description: str