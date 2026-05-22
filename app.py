"""
SAPMigrate — Gradio UI
Offline ABAP code auditor for SAP API Policy v4/2026.

UI strings are in English; model justifications stay in PT-BR
to showcase Gemma 4 31B's technical multilingual capability.
"""
import sys
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent))

import gradio as gr

from parser.abap_parser import extract_sap_calls
from classifier.gemma_classifier import GemmaClassifier, Finding


# Initialize classifier once (model cached in VRAM)
print("🚀 Initializing SAPMigrate...")
classifier = GemmaClassifier()
print("✅ Ready.\n")


SEVERITY_COLORS = {
    "CRITICAL": "🔴",
    "HIGH":     "🟠",
    "MEDIUM":   "🟡",
    "LOW":      "🟢",
}

CLASSIFICATION_BADGE = {
    "INTERNAL":   "❌ INTERNAL",
    "DEPRECATED": "⚠️  DEPRECATED",
    "PUBLISHED":  "✅ PUBLISHED",
    "UNKNOWN":    "❓ UNKNOWN",
    "CUSTOM_REVIEW":  "⚠️ CUSTOM_REVIEW",
}


def audit_folder(files: list, progress=gr.Progress()):
    """
    Receives list of ABAP files, runs parser + classifier, returns findings.
    """
    if not files:
        return (
            "⚠️  No files uploaded.",
            None,
            "",
            "",
        )

    # Collect candidates from all files
    progress(0, desc="Parsing ABAP code...")
    all_candidates = []
    abap_files = [Path(f.name) if hasattr(f, "name") else Path(f) for f in files]
    abap_files = [f for f in abap_files if f.suffix.lower() == ".abap"]

    if not abap_files:
        return ("⚠️  No .abap files found.", None, "", "")

    for f in abap_files:
        code = f.read_text(encoding="utf-8", errors="ignore")
        candidates = extract_sap_calls(code, f.name)
        # filter to high/medium priority
        relevant = [c for c in candidates if c["prioridade_audit"] <= 2]
        all_candidates.extend(relevant)

    if not all_candidates:
        return (
            f"✅ {len(abap_files)} file(s) analyzed. No audit candidates — code appears compliant.",
            None, "", "",
        )

    # Classify each candidate via Gemma 4
    findings = []
    total = len(all_candidates)
    for i, cand in enumerate(all_candidates):
        progress(
            (i + 1) / total,
            desc=f"Classifying {cand['objeto']} ({i+1}/{total})..."
        )
        finding = classifier.classify(cand)
        if finding:
            findings.append(finding)

    # Filter violations only
    violations = [f for f in findings if f.classificacao != "PUBLISHED"]

    # ===== Outputs =====
    # 1. Status text
    counter = Counter(f.severidade for f in violations)
    status = (
        f"📊 **Audit complete** — {len(abap_files)} file(s), "
        f"{len(findings)} calls audited, **{len(violations)} violations**.\n\n"
        f"🔴 Critical: **{counter.get('CRITICAL', 0)}** &nbsp;&nbsp; "
        f"🟠 High: **{counter.get('HIGH', 0)}** &nbsp;&nbsp; "
        f"🟡 Medium: **{counter.get('MEDIUM', 0)}** &nbsp;&nbsp; "
        f"🟢 Low: **{counter.get('LOW', 0)}**"
    )

    # 2. Findings table
    if violations:
        table_rows = [
            [
                SEVERITY_COLORS.get(f.severidade, "") + " " + f.severidade,
                CLASSIFICATION_BADGE.get(f.classificacao, f.classificacao),
                f.arquivo,
                f.numero_linha,
                f.objeto_sap,
                ", ".join(f.alternativas_recomendadas) if f.alternativas_recomendadas else "—",
            ]
            for f in sorted(violations, key=lambda x: (
                {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}.get(x.severidade, 4),
                x.arquivo, x.numero_linha
            ))
        ]
    else:
        table_rows = []

    # 3. Detailed findings (markdown)
    if violations:
        details_md = "## Violation details\n\n"
        for f in violations:
            details_md += (
                f"### {SEVERITY_COLORS.get(f.severidade, '')} `{f.objeto_sap}` "
                f"in `{f.arquivo}:{f.numero_linha}`\n\n"
                f"**Classification:** {CLASSIFICATION_BADGE.get(f.classificacao)} &nbsp;|&nbsp; "
                f"**Severity:** {f.severidade}\n\n"
                f"**Justification (PT-BR):** {f.justificativa}\n\n"
            )
            if f.alternativas_recomendadas:
                details_md += (
                    f"**Recommended alternatives:** "
                    + ", ".join(f"`{a}`" for a in f.alternativas_recomendadas)
                    + "\n\n"
                )
            if f.linha_problematica:
                details_md += f"**Code:** ```{f.linha_problematica}```\n\n"
            details_md += "---\n\n"
    else:
        details_md = "✅ No violations detected."

    # 4. Executive report
    report_md = build_executive_report(abap_files, findings, violations, counter)

    return status, table_rows, details_md, report_md


def build_executive_report(abap_files, findings, violations, counter):
    """Executive report in markdown (English headers, PT-BR justifications inside details only)."""
    compliant = len(findings) - len(violations)
    md = f"""# Audit Report — SAP API Policy v4/2026

**Generated by:** SAPMigrate (Gemma 4 31B Dense, local)
**Files analyzed:** {len(abap_files)}
**SAP calls audited:** {len(findings)} ({compliant} compliant, {len(violations)} in violation)

## Severity distribution

| Severity | Count |
|---|---|
| 🔴 Critical | {counter.get('CRITICAL', 0)} |
| 🟠 High     | {counter.get('HIGH', 0)} |
| 🟡 Medium   | {counter.get('MEDIUM', 0)} |
| 🟢 Low      | {counter.get('LOW', 0)} |

## Remediation priorities

"""
    by_severity = {"CRITICAL": [], "HIGH": [], "MEDIUM": [], "LOW": []}
    for f in violations:
        by_severity.setdefault(f.severidade, []).append(f)

    for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        items = by_severity.get(sev, [])
        if not items:
            continue
        md += f"\n### {SEVERITY_COLORS.get(sev)} {sev}\n\n"
        for f in items:
            alts = ", ".join(f.alternativas_recomendadas) if f.alternativas_recomendadas else "—"
            md += (
                f"- **`{f.objeto_sap}`** in `{f.arquivo}:{f.numero_linha}` "
                f"({CLASSIFICATION_BADGE.get(f.classificacao)})\n"
                f"    - Recommended: {alts}\n"
            )

    md += "\n---\n\n*Report generated offline. No code left this machine.*"
    return md


# ===== Interface =====

with gr.Blocks(title="SAPMigrate", theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        """
        # SAPMigrate
        ### Offline ABAP code auditor for SAP API Policy v4/2026

        100% local. Powered by **Gemma 4 31B Dense**. No code leaves your machine.
        """
    )

    with gr.Row():
        with gr.Column(scale=1):
            files_input = gr.File(
                label="ABAP Files (.abap)",
                file_count="multiple",
                file_types=[".abap"],
            )
            audit_btn = gr.Button("🔍 Audit", variant="primary", size="lg")

        with gr.Column(scale=2):
            status_output = gr.Markdown(label="Status")

    with gr.Tabs():
        with gr.Tab("📋 Findings"):
            findings_table = gr.Dataframe(
                headers=["Severity", "Classification", "File", "Line", "SAP Object", "Recommended"],
                datatype=["str", "str", "str", "number", "str", "str"],
                wrap=True,
                interactive=False,
                column_widths=["100px", "130px", "200px", "60px", "200px", "240px"],
            )

        with gr.Tab("📄 Details"):
            details_output = gr.Markdown()

        with gr.Tab("📊 Executive Report"):
            report_output = gr.Markdown()

    audit_btn.click(
        fn=audit_folder,
        inputs=[files_input],
        outputs=[status_output, findings_table, details_output, report_output],
    )

    gr.Markdown(
        """
        ---
        *SAPMigrate is an educational prototype. It does not replace formal SAP audit.
        The v4/2026 policy must be consulted in the official source.*
        """
    )


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, inbrowser=False)