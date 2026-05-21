"""
Parser pragmático de ABAP. Regex robusta + heurísticas.
Versão 2: trata SELECT multilinha corretamente.
"""
import re
from pathlib import Path

INTERNAL_TABLES = {
    "mara", "makt", "marc", "mard", "mbew",
    "vbak", "vbap", "vbep", "vbrk", "vbrp", "vbfa",
    "kna1", "knb1", "knvv", "lfa1", "lfb1", "lfm1",
    "ekko", "ekpo", "eket", "ekbe",
    "lips", "likp",
    "bseg", "bkpf", "bsid", "bsik",
    "t001", "t001w", "t023",
}

# Padrões single-line (BAPI, UPDATE/INSERT/DELETE simples)
PATTERN_BAPI = re.compile(
    r"CALL\s+FUNCTION\s+['\"]([A-Z_][A-Z0-9_]*)['\"]", re.IGNORECASE
)
PATTERN_UPDATE = re.compile(
    r"(?:UPDATE|INSERT\s+INTO|DELETE\s+FROM)\s+([a-z][a-z0-9_]*)",
    re.IGNORECASE,
)

# Padrão multilinha pra SELECT — opera no arquivo todo
PATTERN_SELECT_MULTILINE = re.compile(
    r"SELECT\b[\s\S]*?\bFROM\s+([a-z][a-z0-9_]*)",
    re.IGNORECASE,
)


def is_comment_line(line: str) -> bool:
    stripped = line.lstrip()
    return stripped.startswith("*") or stripped.startswith('"')


def _strip_comments(abap_code: str) -> str:
    """Remove linhas de comentário e comentários inline."""
    cleaned_lines = []
    for line in abap_code.splitlines():
        if is_comment_line(line):
            cleaned_lines.append("")  # preserva contagem de linhas
        else:
            # remove comentário inline (tudo depois de " que não esteja em string)
            # Simplificação: assume " só aparece em comentário (não é 100% correto mas serve)
            quote_idx = line.find('"')
            if quote_idx >= 0:
                cleaned_lines.append(line[:quote_idx])
            else:
                cleaned_lines.append(line)
    return "\n".join(cleaned_lines)


def _line_number_at_offset(text: str, offset: int) -> int:
    """Dado um offset de caractere no texto, retorna número da linha (1-indexed)."""
    return text[:offset].count("\n") + 1


def _extract_statement_around(text: str, start_offset: int, max_chars: int = 400) -> str:
    """Extrai trecho de código a partir do offset até encontrar ponto final ou max_chars."""
    end = start_offset
    while end < len(text) and end - start_offset < max_chars:
        if text[end] == "." and (end + 1 >= len(text) or text[end + 1] in "\n \t"):
            end += 1
            break
        end += 1
    snippet = text[start_offset:end]
    # Compacta whitespace pra ficar legível
    return " ".join(snippet.split())


def _priority(tipo: str, obj: str) -> int:
    obj_lower = obj.lower()
    if tipo in ("select_table", "update_table") and obj_lower in INTERNAL_TABLES:
        return 1
    if tipo == "z_function":
        return 2
    if tipo in ("select_table", "update_table", "bapi_call"):
        return 2
    return 3


def extract_sap_calls(abap_code: str, filename: str) -> list[dict]:
    """
    Extrai chamadas SAP do código ABAP.
    """
    # Limpa comentários preservando contagem de linhas
    cleaned = _strip_comments(abap_code)

    candidates = []

    # 1. BAPI / function calls (single-line)
    for match in PATTERN_BAPI.finditer(cleaned):
        obj_name = match.group(1).upper()
        tipo = "z_function" if obj_name.startswith(("Z", "Y")) else "bapi_call"
        line_num = _line_number_at_offset(cleaned, match.start())
        candidates.append({
            "tipo": tipo,
            "objeto": obj_name,
            "arquivo": filename,
            "linha": line_num,
            "codigo": _extract_statement_around(cleaned, match.start()),
            "prioridade_audit": _priority(tipo, obj_name),
        })

    # 2. SELECT statements (multilinha) — opera no texto inteiro
    for match in PATTERN_SELECT_MULTILINE.finditer(cleaned):
        table = match.group(1).lower()
        line_num = _line_number_at_offset(cleaned, match.start())
        candidates.append({
            "tipo": "select_table",
            "objeto": table.upper(),
            "arquivo": filename,
            "linha": line_num,
            "codigo": _extract_statement_around(cleaned, match.start()),
            "prioridade_audit": _priority("select_table", table),
        })

    # 3. UPDATE / INSERT / DELETE (single-line — suficiente pra MVP)
    for match in PATTERN_UPDATE.finditer(cleaned):
        table = match.group(1).lower()
        line_num = _line_number_at_offset(cleaned, match.start())
        candidates.append({
            "tipo": "update_table",
            "objeto": table.upper(),
            "arquivo": filename,
            "linha": line_num,
            "codigo": _extract_statement_around(cleaned, match.start()),
            "prioridade_audit": _priority("update_table", table),
        })

    # Dedup por (arquivo, linha, objeto)
    seen = set()
    unique = []
    for c in candidates:
        key = (c["arquivo"], c["linha"], c["objeto"])
        if key not in seen:
            seen.add(key)
            unique.append(c)

    # Ordena por linha
    unique.sort(key=lambda c: c["linha"])

    return unique


def parse_folder(folder_path: str) -> list[dict]:
    folder = Path(folder_path)
    all_candidates = []
    for abap_file in folder.glob("*.abap"):
        code = abap_file.read_text(encoding="utf-8")
        candidates = extract_sap_calls(code, abap_file.name)
        all_candidates.extend(candidates)
    return all_candidates


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Uso: python parser/abap_parser.py <pasta_ou_arquivo.abap>")
        sys.exit(1)

    target = Path(sys.argv[1])
    if target.is_file():
        code = target.read_text()
        candidates = extract_sap_calls(code, target.name)
    else:
        candidates = parse_folder(str(target))

    print(f"\n{len(candidates)} candidatos:\n")
    for c in candidates:
        print(f"  [{c['prioridade_audit']}] {c['arquivo']}:{c['linha']} "
              f"[{c['tipo']}] {c['objeto']}")
        print(f"      → {c['codigo'][:100]}...")
