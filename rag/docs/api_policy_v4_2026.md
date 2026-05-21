# SAP API Policy v4/2026

Published: April 2026

## Section 1: Scope and Purpose

The SAP API Policy v4/2026 governs how integrations, custom code, and AI-driven
tools may access SAP systems including S/4HANA Cloud (Public and Private Edition),
S/4HANA on-premise, SAP Business Network, Ariba, and SuccessFactors.

## Section 2: Published vs Internal APIs

A published API is one that meets ALL of the following criteria:
- Listed in the SAP Business Accelerator Hub (api.sap.com), OR identified as
  released in the official product documentation (help.sap.com)
- Has a documented contract, parameters, and stable signature
- Is covered by SAP's compatibility and support guarantees

Internal APIs include:
- Direct read or write access to underlying database tables via SELECT, INSERT,
  UPDATE, DELETE statements in custom ABAP code (e.g., MARA, BSEG, EKKO, VBAK,
  KNA1, LFA1, MARC, MARD)
- Function modules and RFCs not listed in the Business Accelerator Hub
- Internal classes, methods, and CDS views marked as @AccessControl.private
- Customer-namespace (Z*, Y*) function modules with undocumented signatures

## Section 3: Prohibitions

### 3.1 Direct Database Access
Direct read access to underlying database tables via SELECT statements in
custom ABAP code bypasses the published API layer and is prohibited under
API Policy v4/2026. Customers must use released APIs or CDS Views exposed
via OData.

### 3.2 Non-published Function Modules
CALL FUNCTION statements invoking function modules that are not listed in the
SAP Business Accelerator Hub or marked as released in product documentation
constitute non-published API usage and are prohibited.

### 3.3 Deprecated APIs
APIs flagged as deprecated in SAP product documentation must not be used in
new developments. Existing usage must be remediated according to the
recommended replacement listed in the corresponding SAP Note.

## Section 4: Compliance Obligations

Customers are responsible for auditing their custom code base for non-published
API usage. Remediation priority should follow:
1. Business criticality of the integration
2. Frequency of upgrade cycles (S/4HANA Cloud Public Edition: urgent)
3. Risk of breakage on next SAP release

## Section 5: Clean Core Principle

The Clean Core principle, established under API Policy v4/2026, states that
customer extensions should reside outside the SAP S/4HANA core system, ideally
on SAP Business Technology Platform (BTP). Custom extensions communicate with
the core exclusively through published APIs and events.
