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

## Customer Z* Code Review Patterns

### When Z* function modules need review
Customer-namespace (Z*) function modules are NOT automatically prohibited under
v4/2026 — they are customer-developed code and remain customer IP. However, Z*
modules should be flagged for CUSTOM_REVIEW when any of the following applies:

1. The Z* function wraps a non-published SAP API (direct internal API call inside)
2. The Z* function performs direct access to SAP standard tables
3. The Z* function name suggests business logic that has a released SAP equivalent
   (e.g., Z_PRICING_CALC where API_PRICING_PROCEDURE_SRV exists)
4. The Z* function has no documentation regarding its dependencies

For pricing-related Z* RFCs specifically, consider whether the released API
API_PRICING_PROCEDURE_SRV could replace custom logic. This is a review
recommendation, not a violation.

## Migration Priority Matrix

| Pattern | Severity | Action |
|---------|----------|--------|
| Direct SELECT on standard tables | CRITICAL | Immediate remediation |
| Deprecated BAPI calls | HIGH | Plan migration within 6 months |
| Z* function modules without docs | MEDIUM | Audit and document, then migrate |
| Released BAPI usage | LOW | None — compliant |
