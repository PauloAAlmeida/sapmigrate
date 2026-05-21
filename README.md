# SAPMigrate

> Offline ABAP code auditor for SAP API Policy v4/2026 — powered by Gemma 4 31B Dense, running 100% locally.

[![Gemma 4 Challenge](https://img.shields.io/badge/Gemma%204-Challenge-blue)](https://dev.to/t/gemmachallenge)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Ollama](https://img.shields.io/badge/Ollama-Gemma%204%2031B-orange)](https://ollama.com)

---

## The problem

In **April 2026**, SAP published the **API Policy v4/2026**, restricting the use of internal APIs in customer code:

- Direct access to standard tables (`MARA`, `BSEG`, `VBAK`, `KNA1`, etc.) is prohibited.
- Deprecated BAPIs (e.g., `BAPI_CUSTOMER_CREATEFROMDATA1`) must be replaced.
- Undocumented `Z*` function modules violate the Clean Core principle.

Companies with large ABAP codebases now need to audit their code to find these violations **before the next S/4HANA upgrade breaks them**. Today this work is manual, time-consuming and expensive — typically done by senior SAP consultants at premium hourly rates.

And here is the twist: **sending proprietary ABAP code to cloud-based LLMs is not an option.** It is intellectual property, often under NDA, subject to GDPR / LGPD / SOX restrictions in multinationals. The new policy itself acknowledges this — it explicitly tightens how SAP data can be accessed at scale, including by AI-driven tools.

This is one of those rare cases where **local-first AI is not a preference. It is a contractual requirement.**

## The solution

SAPMigrate is a working prototype that demonstrates how this type of audit can run **entirely on the auditor's machine**:

1. **ABAP parser** extracts SAP call sites (BAPIs, `SELECT`s on standard tables, `Z*` RFCs).
2. **RAG** over a curated snapshot of SAP documentation retrieves relevant context via ChromaDB + multilingual embeddings.
3. **Gemma 4 31B Dense** (running locally via Ollama) classifies each call as `PUBLISHED`, `INTERNAL`, `DEPRECATED`, or `UNKNOWN`.
4. The model suggests v4/2026-compliant alternatives and justifies its decision **in Brazilian Portuguese**, citing the exact documents that support it.
5. The system generates an executive report grouped by remediation priority.

**No line of code ever leaves the auditor's machine.**

## Why this is interesting

- **Genuine use case for local-first LLMs.** Most "local AI" demos are nice-to-haves. Here, local execution is forced by the constraints of the domain.
- **Real policy, real timing.** The v4/2026 policy was published in April 2026; this project was built 6 weeks later, in May 2026.
- **Multilingual technical capability.** Headers are in English (for international auditors); the model's justifications are in Brazilian Portuguese. This intentionally showcases Gemma 4 31B Dense's ability to produce dense technical reasoning in PT-BR at publication quality — a meaningful differentiator for non-English markets.
- **Honest scope.** This is a proof of concept, not a finished product. Limitations are declared openly (see below).

## Screenshots

### Findings table
Sortable view of violations across the codebase, color-coded by severity.

![Findings](docs/screenshots/findings.png)

### Detail view
Each finding includes the LLM's justification in Brazilian Portuguese, citing the documents that support the decision.

![Details](docs/screenshots/details.png)

### Executive report
Auto-generated markdown report grouped by remediation priority.

![Executive Report](docs/screenshots/executive_report.png)

## Stack

| Layer | Component |
|---|---|
| LLM | Gemma 4 31B Dense (`gemma4:31b` via Ollama) |
| Embeddings | `intfloat/multilingual-e5-base` |
| Vector store | ChromaDB (persistent, local) |
| Parser | Python regex + AST-aware heuristics |
| UI | Gradio (English headers, PT-BR justifications) |
| Validation | Pydantic v2 |
| Hardware tested | NVIDIA RTX 5090 (32 GB VRAM) |

## Why Gemma 4 31B Dense (and not E2B / E4B / 26B MoE)

The choice is deliberate and central to the project. Of the four Gemma 4 variants:

- **E2B / E4B**: insufficient for dense technical reasoning over ABAP + retrieved SAP documentation. Hallucinates rare patterns. Cannot reliably distinguish `DEPRECATED` from `INTERNAL`.
- **26B MoE**: viable alternative, but routing variance reduces predictability for structured-output tasks. For an auditing tool, deterministic JSON output matters.
- **31B Dense**: the sweet spot for this use case. Comfortable in ~20 GB of VRAM, predictable output, strong technical reasoning, native multilingual capability that produces PT-BR justifications matching the quality of a senior auditor's report.

The **256K context window** is critical: each classification prompt includes the system instructions, the code excerpt, up to 5 RAG-retrieved excerpts, and few-shot examples — comfortably under the limit, no chunk-juggling needed.

## How to run

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com) installed (Windows, Linux, or macOS)
- GPU with 20+ GB VRAM (tested on RTX 5090)
- ~25 GB of disk for the Gemma 4 31B model

### Installation

```bash
git clone https://github.com/PauloAAlmeida/sapmigrate.git
cd sapmigrate

# Create venv
python3 -m venv .venv
source .venv/bin/activate  # Linux/WSL/macOS
# or: .venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Pull Gemma 4 31B (one-time, ~19 GB download)
ollama pull gemma4:31b

# Build the RAG index from curated docs (one-time)
python rag/ingest.py

# Launch the UI
python app.py
```

Open <http://localhost:7860> in your browser, drag-and-drop ABAP files into the upload area, and click **Audit**.

### Try it with the demo dataset

The `demo/` folder contains 6 small ABAP files covering all four classifications (PUBLISHED, INTERNAL, DEPRECATED, UNKNOWN). After launching the UI, upload all 6 files and you should see **6 violations across 4 files**, with severity ranging from CRITICAL (direct table access) to MEDIUM (deprecated BAPI with clear replacement).

### Note on environment variables

If Ollama is running on Windows and you call from WSL2, you may need to point the client at the Windows host:

```bash
export OLLAMA_HOST="http://$(ip route show | grep -i default | awk '{print $3}'):11434"
```

## Architecture


┌──────────────────┐
    │  ABAP file(s)    │
    └────────┬─────────┘
             │
             ▼
    ┌──────────────────┐
    │  Parser (regex)  │   extracts BAPI / SELECT / Z* call sites
    └────────┬─────────┘
             │
             ▼
    ┌──────────────────┐
    │  RAG retriever   │   top-k SAP doc chunks (ChromaDB)
    └────────┬─────────┘
             │
             ▼
    ┌──────────────────┐
    │  Gemma 4 31B     │   classifies + justifies (PT-BR)
    │     (local)      │
    └────────┬─────────┘
             │
             ▼
    ┌──────────────────┐
    │ Pydantic Finding │   structured, validated output
    └────────┬─────────┘
             │
             ▼
    ┌──────────────────┐
    │  Gradio UI       │   findings + details + report
    └──────────────────┘

## On the RAG corpus

By default, SAPMigrate ships with a **small curated snapshot** of SAP documentation in `rag/docs/`:

- `api_policy_v4_2026.md` — synthesis of the policy
- `business_accelerator_hub.md` — reference list of released APIs
- `clean_core_principles.md` — Clean Core architectural rules
- `deprecated_apis.md` — migration reference for legacy patterns

These documents are written **by the author** based on public SAP information, formatted for retrieval purposes. They are not redistributions of SAP-proprietary content.

For a production-grade audit, you would replace this with a real snapshot of:
- [SAP Business Accelerator Hub](https://api.sap.com)
- [SAP Help Portal](https://help.sap.com)
- Relevant SAP Notes for the modules your organization uses

The pipeline is designed so that swapping the contents of `rag/docs/` and re-running `python rag/ingest.py` is enough to adapt the auditor to your organization's specific SAP landscape.

## Limitations (honest scope)

This is a proof of concept. Known limitations:

- **Regex-based parser, not full AST.** Misses edge cases such as dynamic calls (`CALL FUNCTION lv_name`) and complex macros.
- **Small synthetic demo set.** Real ABAP codebases have 10x more noise; the prototype's recall on real-world code has not been measured.
- **Static snapshot of SAP docs.** No live tracking of SAP Notes or product release changes.
- **No tested support for non-ABAP code paths** (e.g., SAP CPI flows, JCo Java integrations). The architecture supports this but it is not implemented.
- **PT-BR justifications only.** A multilingual UI (EN/DE justifications) would be straightforward to add but is not in scope.

This tool reduces a senior SAP auditor's time, it does not replace them.

## What I learned about Gemma 4 31B Dense

Working notes from building this prototype:

1. **JSON output is solid out of the box.** With `format="json"` and `temperature=0.1`, all 8 demo classifications produced valid JSON parseable by Pydantic with zero retries.
2. **Deterministic enough for product use.** Re-running the same input twice produced identical classifications and severity scores. Justification wording varies slightly, which is acceptable.
3. **PT-BR technical fluency is real.** The model produces sentences like *"O acesso direto à tabela MARA via SELECT é explicitamente proibido pela política v4/2026"* — terminology, structure, and tone match a senior auditor's report.
4. **Reasoning in layers.** In one test case (`Z_CUSTOM_BUSINESS_RULE`), the model identified that the Migration Priority Matrix would assign `MEDIUM` severity to Z* functions without documentation — but elevated to `HIGH` because the function name suggested critical business logic. It justified the elevation explicitly. Smaller models do not do this.
5. **256K context is comfortable.** No need for chunk-juggling when combining system prompt + code + 5 RAG snippets + few-shots.

## Roadmap

If extended beyond a proof of concept:

- Full ABAP AST parser (ANTLR-based)
- Live SAP Notes / Accelerator Hub integration via authenticated APIs
- Patch generation for common migration patterns (BAPI swap, OData wrapper)
- CI/CD gate mode: block merges on `CRITICAL` findings
- Support for SAP CPI flows, JCo Java integrations
- Multilingual justifications (EN, DE) selectable per user

## License

[MIT](LICENSE). Use at your own risk.

## Acknowledgements

- Submission for the [Gemma 4 Challenge](https://dev.to/t/gemmachallenge) by [DEV Community](https://dev.to) and Google.
- SAP documentation references are public; this project does not redistribute SAP-proprietary content.

---

**Author:** Paulo Reis ([@PauloAAlmeida](https://github.com/PauloAAlmeida)) — Applied Scientist, working on RAG in dense technical domains (legal, financial).
