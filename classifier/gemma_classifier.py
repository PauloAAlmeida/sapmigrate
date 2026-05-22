"""
Classifier: pra cada candidato do parser, busca contexto via RAG e
classifica usando Gemma 4 31B.
"""
import sys
import json
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

import ollama
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from pydantic import BaseModel, Field, ValidationError

from config import (
    CHROMA_PATH, EMBED_MODEL, GEMMA_MODEL, OLLAMA_HOST, TOP_K_RETRIEVAL
)


# ============================================================
# Schemas (Pydantic)
# ============================================================

class Finding(BaseModel):
    objeto_sap: str
    classificacao: str  # PUBLISHED | INTERNAL | DEPRECATED | UNKNOWN
    severidade: str    # LOW | MEDIUM | HIGH | CRITICAL
    alternativas_recomendadas: list[str] = Field(default_factory=list)
    justificativa: str
    linha_problematica: Optional[str] = None
    # Metadados anexados pelo classifier (não vêm do LLM)
    arquivo: Optional[str] = None
    numero_linha: Optional[int] = None
    tipo_chamada: Optional[str] = None


# ============================================================
# RAG retriever
# ============================================================

class SAPDocRetriever:
    def __init__(self):
        embed_fn = SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        self.collection = client.get_collection("sap_docs", embedding_function=embed_fn)

    def retrieve(self, query: str, k: int = TOP_K_RETRIEVAL) -> list[dict]:
        results = self.collection.query(query_texts=[query], n_results=k)
        docs = results["documents"][0]
        metas = results["metadatas"][0]
        return [
            {"texto": doc, "fonte": meta.get("source", "unknown")}
            for doc, meta in zip(docs, metas)
        ]


# ============================================================
# Prompts
# ============================================================

SYSTEM_PROMPT = """You are an auditor specialized in SAP API Policy v4/2026 (published April 2026).
Your task is to classify ABAP/Python/Java code excerpts for compliance with the policy, which states:

- PUBLISHED APIs (listed in SAP Business Accelerator Hub or official product documentation) are allowed.
- INTERNAL APIs (direct table access, undocumented classes, private RFCs) are prohibited under v4/2026.
- DEPRECATED APIs (published but marked obsolete with a recommended replacement) violate the Clean Core principle.
- UNKNOWN when there is insufficient information in the documents to classify.
- CUSTOM_REVIEW for customer-namespace (Z*, Y*) code that is not automatically prohibited but should be reviewed by a human auditor (e.g., undocumented Z*
  that may wrap non-published APIs, or Z* whose business logic has a released
  SAP equivalent).

You receive: (a) the code excerpt under analysis, (b) relevant excerpts retrieved from official SAP documentation via RAG.

Respond ONLY in valid JSON with this structure:
{
  "objeto_sap": "<name of the BAPI/table/class identified>",
  "classificacao": "PUBLISHED" | "INTERNAL" | "DEPRECATED" | "UNKNOWN" | "CUSTOM_REVIEW",
  "severidade": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
  "alternativas_recomendadas": ["<name of substitute>", ...],
  "justificativa": "<2-3 sentences IN BRAZILIAN PORTUGUESE (PT-BR) explicitly citing the documentation excerpt that supports the decision>",
  "linha_problematica": "<the exact code line violating, or null if OK>"
}

IMPORTANT: The `justificativa` field MUST be written in Brazilian Portuguese (PT-BR), 
even though this prompt is in English. All other field values stay in English (classification, severity, object names).

Severity calibration:
- LOW: compliant code (PUBLISHED)
- MEDIUM: deprecated with clear replacement, low risk
- HIGH: deprecated in critical use OR Z* without documentation
- CRITICAL: direct internal table access explicitly prohibited by v4/2026
"""

def build_user_prompt(candidate: dict, docs: list[dict]) -> str:
    docs_section = "\n\n".join(
        f"[Document {i+1} — {d['fonte']}]\n{d['texto']}"
        for i, d in enumerate(docs)
    )
    return f"""Code under analysis:

{candidate['codigo']}

SAP object identified: {candidate['objeto']}
Call type: {candidate['tipo']}

Excerpts retrieved from SAP documentation:

{docs_section}

Classify the code above. Remember: justificativa MUST be in PT-BR."""

# ============================================================
# Classifier principal
# ============================================================

class GemmaClassifier:
    def __init__(self, model: str = GEMMA_MODEL, host: str = OLLAMA_HOST):
        self.model = model
        self.client = ollama.Client(host=host)
        self.retriever = SAPDocRetriever()

    def classify(self, candidate: dict, verbose: bool = False) -> Optional[Finding]:
        """
        Roda RAG + LLM pra um candidato. Retorna Finding ou None se falhar.
        """
        # 1. RAG
        query = f"{candidate['objeto']} {candidate['tipo']}"
        docs = self.retriever.retrieve(query)

        if verbose:
            print(f"\n  🔍 RAG query: {query}")
            for d in docs:
                print(f"     → {d['fonte']}: {d['texto'][:80]}...")

        # 2. LLM
        user_prompt = build_user_prompt(candidate, docs)
        try:
            response = self.client.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                options={"temperature": 0.1},
                format="json",
            )
            raw = response["message"]["content"]
        except Exception as e:
            print(f"  ❌ Erro no Ollama pra {candidate['objeto']}: {e}")
            return None

        # 3. Parse + validação Pydantic
        try:
            parsed = json.loads(raw)
            finding = Finding(
                objeto_sap=parsed.get("objeto_sap", candidate["objeto"]),
                classificacao=parsed.get("classificacao", "UNKNOWN"),
                severidade=parsed.get("severidade", "MEDIUM"),
                alternativas_recomendadas=_normalize_alternatives(
                    parsed.get("alternativas_recomendadas") or
                    parsed.get("alternativa_recomendada")
                ),
                justificativa=parsed.get("justificativa", ""),
                linha_problematica=parsed.get("linha_problematica"),
                arquivo=candidate["arquivo"],
                numero_linha=candidate["linha"],
                tipo_chamada=candidate["tipo"],
            )
            return finding
        except (json.JSONDecodeError, ValidationError) as e:
            print(f"  ⚠️  Falha de parse pra {candidate['objeto']}: {e}")
            print(f"      Raw: {raw[:200]}")
            return None


def _normalize_alternatives(value) -> list[str]:
    """Aceita string única, lista, ou None — sempre retorna lista."""
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value.strip() else []
    if isinstance(value, list):
        return [str(v) for v in value if v]
    return []


# ============================================================
# CLI de teste
# ============================================================

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python classifier/gemma_classifier.py <arquivo.abap>")
        sys.exit(1)

    from parser.abap_parser import extract_sap_calls

    target = Path(sys.argv[1])
    code = target.read_text()
    candidates = extract_sap_calls(code, target.name)

    print(f"\n📋 {len(candidates)} candidatos a auditar em {target.name}\n")

    classifier = GemmaClassifier()
    findings = []
    for i, cand in enumerate(candidates, 1):
        print(f"\n[{i}/{len(candidates)}] Auditando {cand['objeto']} (linha {cand['linha']})...")
        finding = classifier.classify(cand, verbose=True)
        if finding:
            findings.append(finding)
            print(f"\n  ✅ {finding.classificacao} | {finding.severidade}")
            print(f"     Alternativas: {finding.alternativas_recomendadas or 'n/a'}")
            print(f"     Justificativa: {finding.justificativa}")

    # Filtra só os não-compliant
    violations = [f for f in findings if f.classificacao != "PUBLISHED"]

    print(f"\n{'='*60}")
    print(f"📊 RESUMO: {len(violations)} violações de {len(findings)} análises")
    print(f"{'='*60}")

    for f in violations:
        print(f"\n  [{f.severidade}] {f.arquivo}:{f.numero_linha} — {f.objeto_sap}")
        print(f"    Classificação: {f.classificacao}")
        if f.alternativas_recomendadas:
            print(f"    Use em vez disso: {', '.join(f.alternativas_recomendadas)}")
