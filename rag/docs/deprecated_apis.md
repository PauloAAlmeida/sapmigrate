# Deprecated SAP APIs — Migration Reference

## Customer Master (Deprecated under Business Partner approach)

### BAPI_CUSTOMER_CREATEFROMDATA1
- Status: DEPRECATED
- Deprecated since: S/4HANA 1511
- SAP Note: 2270333
- Reason: Replaced by Business Partner approach
- Replacement: BAPI_BUPA_CREATE_FROM_DATA or OData API_BUSINESS_PARTNER
- Compliance: Use in new code violates Clean Core under v4/2026

As of S/4HANA 1511, the customer/vendor data model has been replaced by
the Business Partner approach. BAPI_CUSTOMER_CREATEFROMDATA1 is deprecated
and will not be enhanced. New developments must use BAPI_BUPA_CREATE_FROM_DATA
or the released OData service API_BUSINESS_PARTNER.

### BAPI_CUSTOMER_CHANGEFROMDATA
- Status: DEPRECATED
- Reason: Replaced by Business Partner approach
- Replacement: BAPI_BUPA_CHANGE_FROM_DATA

### KNA1 and KNB1 Table Access
The legacy customer master tables KNA1 and KNB1 remain technically available
for backward compatibility, but their use in new code violates the Clean
Core principle established in API Policy v4/2026.

## Vendor Master (Deprecated under Business Partner approach)

### BAPI_VENDOR_CREATE
- Status: DEPRECATED
- Reason: Replaced by Business Partner approach
- Replacement: BAPI_BUPA_CREATE_FROM_DATA

### LFA1 and LFB1 Table Access
Legacy vendor master tables. Same deprecation status as customer master tables.

## Pricing (Legacy)

### Internal Z-namespace Pricing RFCs
Function modules in the Z* customer namespace that perform pricing calculations
are typically not documented in the Business Accelerator Hub and constitute
INTERNAL or UNKNOWN APIs under v4/2026. These should be reviewed and either:
1. Replaced with released SAP pricing APIs (API_PRICING_PROCEDURE_SRV)
2. Refactored as BTP-side logic consuming released APIs

## Migration Priority Matrix

| Pattern | Severity | Action |
|---------|----------|--------|
| Direct SELECT on standard tables | CRITICA | Immediate remediation |
| Deprecated BAPI calls | ALTA | Plan migration within 6 months |
| Z* function modules without docs | MEDIA | Audit and document, then migrate |
| Released BAPI usage | BAIXA | None — compliant |
