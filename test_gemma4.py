import ollama
import json

SYSTEM_PROMPT = """Você é um auditor especializado em SAP API Policy v4/2026 (publicada em 
abril de 2026). Sua tarefa é classificar trechos de código ABAP/Python/Java
quanto à conformidade com a política, que estabelece:

- APIs PUBLICADAS (listadas no SAP Business Accelerator Hub ou documentação 
  oficial do produto) são permitidas.
- APIs INTERNAS (acesso direto a tabelas, classes não documentadas, RFCs 
  privados) são proibidas pela v4/2026.
- APIs DEPRECADAS (publicadas mas marcadas como obsoletas com substituta 
  recomendada) violam o princípio Clean Core.

Você recebe: (a) o trecho de código sob análise, (b) trechos relevantes 
recuperados da documentação oficial SAP via RAG.

Responda APENAS em JSON válido com a estrutura:
{
  "objeto_sap": "<nome do BAPI/tabela/classe identificado>",
  "classificacao": "PUBLISHED" | "INTERNAL" | "DEPRECATED" | "UNKNOWN",
  "severidade": "BAIXA" | "MEDIA" | "ALTA" | "CRITICA",
  "alternativa_recomendada": "<nome do substituto, ou null se não aplicável>",
  "justificativa": "<2-3 frases em PT-BR citando explicitamente o trecho da documentação que embasa a decisão>",
  "linha_problematica": "<a linha exata de código que viola, ou null se está OK>"
}
"""

CASOS = {
    "caso_1_published": """Código sob análise:

  DATA: ls_poheader TYPE bapimepoheader,
        ls_return   TYPE bapiret2.
  
  ls_poheader-comp_code = 'BR01'.
  ls_poheader-doc_type  = 'NB'.
  
  CALL FUNCTION 'BAPI_PO_CREATE1'
    EXPORTING
      poheader = ls_poheader
    IMPORTING
      return   = ls_return.

Trechos recuperados da documentação SAP:

[Documento 1 — SAP Business Accelerator Hub, BAPI_PO_CREATE1]
"BAPI_PO_CREATE1 is a released, public API for creating purchase orders 
in SAP S/4HANA and ECC. Status: Released for customer use. Last updated: 
2025-11. Recommended for integration scenarios involving procurement."

[Documento 2 — SAP Help Portal, Purchasing BAPIs Overview]
"The BAPI_PO_* family includes BAPI_PO_CREATE1, BAPI_PO_CHANGE, and 
BAPI_PO_GETDETAIL1. These are the supported public interfaces for purchase 
order operations under SAP API Policy v4/2026."

Classifique o código acima.""",

    "caso_2_internal": """Código sob análise:

  DATA: lt_mara TYPE TABLE OF mara.
  
  SELECT matnr mtart matkl FROM mara 
    INTO CORRESPONDING FIELDS OF TABLE lt_mara
    WHERE mtart = 'FERT'.
  
  LOOP AT lt_mara INTO DATA(ls_mara).
    WRITE: / ls_mara-matnr.
  ENDLOOP.

Trechos recuperados da documentação SAP:

[Documento 1 — SAP API Policy v4/2026, Section 3.2]
"Direct read access to underlying database tables (e.g., MARA, BSEG, EKKO) 
via SELECT statements in custom ABAP code bypasses the published API layer 
and is prohibited under API Policy v4/2026. Customers must use released 
APIs or CDS Views exposed via OData."

[Documento 2 — SAP Business Accelerator Hub, Material Master APIs]
"For material master data access, use the released API_MATERIAL_STOCK_SRV 
or the CDS view I_Material. The API_PRODUCT_SRV provides full CRUD 
operations on product master data including the fields previously 
accessed via the MARA table."

Classifique o código acima.""",

    "caso_3_deprecated": """Código sob análise:

  DATA: ls_customer TYPE bapikna101,
        ls_return   TYPE bapiret2.
  
  CALL FUNCTION 'BAPI_CUSTOMER_CREATEFROMDATA1'
    EXPORTING
      pi_customerdata = ls_customer
    IMPORTING
      return          = ls_return.

Trechos recuperados da documentação SAP:

[Documento 1 — SAP Note 2270333, Business Partner Approach]
"As of S/4HANA 1511, the customer/vendor data model has been replaced by 
the Business Partner approach. BAPI_CUSTOMER_CREATEFROMDATA1 is deprecated 
and will not be enhanced. New developments must use BAPI_BUPA_CREATE_FROM_DATA 
or the released OData service API_BUSINESS_PARTNER."

[Documento 2 — SAP Help Portal, Customer-Vendor Integration]
"The legacy customer master tables (KNA1, KNB1) and corresponding BAPIs 
remain technically available for backward compatibility, but their use 
in new code violates the Clean Core principle established in API Policy 
v4/2026."

Classifique o código acima.""",
}

MODEL = "gemma4:31b"

for nome, prompt in CASOS.items():
    print(f"\n{'=' * 60}")
    print(f"  {nome.upper()}")
    print('=' * 60)
    
    response = ollama.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        options={"temperature": 0.1},
        format="json",
    )
    
    raw = response["message"]["content"]
    try:
        parsed = json.loads(raw)
        print(json.dumps(parsed, indent=2, ensure_ascii=False))
    except json.JSONDecodeError:
        print("⚠️ JSON inválido. Output bruto:")
        print(raw)
