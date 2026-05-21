# Clean Core Principles for SAP Extensions

## Definition

The Clean Core paradigm, formalized under SAP API Policy v4/2026, defines
the architectural principle that customer-specific extensions must NOT
modify the SAP S/4HANA core system directly. All extensions communicate
with the core through published APIs and events only.

## Prohibited Patterns

### Direct Table Access
SELECT, INSERT, UPDATE, DELETE statements against SAP standard tables
(MARA, BSEG, EKKO, VBAK, KNA1, LFA1, MARC, MARD, EKPO, VBAP, BKPF, etc.)
in custom ABAP code violate Clean Core. These tables remain technically
accessible for backward compatibility, but their use in new code violates
the Clean Core principle established in API Policy v4/2026.

### Modification of SAP Standard Code
Direct modification of SAP-delivered ABAP programs, function modules,
or classes via repair, modification assistant, or enhancement framework
violates Clean Core.

### Use of Deprecated APIs in New Code
While deprecated APIs remain technically functional, their use in newly
developed code violates Clean Core. Existing usage should be flagged
for remediation.

## Recommended Patterns

### Side-by-Side Extensions on BTP
Customer logic should reside on SAP Business Technology Platform (BTP),
communicating with S/4HANA via released OData/REST APIs.

### Released APIs Only
All integration with the core must go through APIs listed in the SAP
Business Accelerator Hub or explicitly marked as released in product
documentation.

### Wrapper Pattern for Legacy Integrations
When migrating legacy integrations that depend on non-released APIs,
the recommended pattern is to build a wrapper layer on BTP that exposes
the required functionality through a clean, released interface.

## Examples of Compliant Code

### Cloud-native API consumption (ABAP)
Using cl_web_http_client_manager to call released OData endpoints is a
fully compliant pattern. Calls to /sap/opu/odata/sap/API_PRODUCT_SRV/A_Product
follow the Clean Core principle as the customer code does not directly
access the underlying MARA table.

### Released BAPI usage
Calling BAPI_PO_CREATE1, BAPI_SALESORDER_CREATEFROMDAT2, or other
released BAPIs through standard CALL FUNCTION mechanism is compliant.
