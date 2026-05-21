from pydantic import BaseModel, Field
from typing import Literal, Optional
from enum import Enum

class Classification(str, Enum):
    PUBLISHED = "PUBLISHED"
    INTERNAL = "INTERNAL"
    DEPRECATED = "DEPRECATED"
    UNKNOWN = "UNKNOWN"

class Severity(str, Enum):
    BAIXA = "BAIXA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"
    CRITICA = "CRITICA"

class Finding(BaseModel):
    objeto_sap: str = Field(..., description="Nome do BAPI/tabela/classe")
    classificacao: Classification
    severidade: Severity
    alternativas_recomendadas: list[str] = Field(default_factory=list)
    justificativa: str = Field(..., min_length=20)
    linha_problematica: Optional[str] = None
    arquivo: str
    numero_linha: Optional[int] = None

