# SAP Business Accelerator Hub — Released APIs Reference

## Purchase Order Management

### BAPI_PO_CREATE1
- Status: Released for customer use
- Last updated: 2025-11
- Description: Creates a purchase order in SAP S/4HANA and ECC
- Recommended for: integration scenarios involving procurement
- Compliance: Compliant with API Policy v4/2026

### BAPI_PO_CHANGE
- Status: Released for customer use
- Description: Modifies an existing purchase order
- Compliance: Compliant with API Policy v4/2026

### BAPI_PO_GETDETAIL1
- Status: Released for customer use
- Description: Retrieves purchase order header and item details
- Compliance: Compliant with API Policy v4/2026

The BAPI_PO_* family includes BAPI_PO_CREATE1, BAPI_PO_CHANGE, and
BAPI_PO_GETDETAIL1. These are the supported public interfaces for purchase
order operations under SAP API Policy v4/2026.

## Sales Order Management

### BAPI_SALESORDER_CREATEFROMDAT2
- Status: Released for customer use
- Description: Creates a sales order
- Compliance: Compliant with API Policy v4/2026

### API_SALES_ORDER_SRV (OData)
- Status: Released (modern alternative)
- Endpoint: /sap/opu/odata/sap/API_SALES_ORDER_SRV
- Description: REST/OData service for sales order CRUD operations
- Recommended for: cloud-native integrations

### A_SalesOrder (CDS View) e API_SALES_ORDER_SRV
- Status: Released
- Description: Read access to sales order header and item data
- Replaces: direct access to VBAK, VBAP, VBEP tables
- Compliance: Mandatory replacement under v4/2026 for sales document access

## Material Master Data

### API_PRODUCT_SRV (OData)
- Status: Released
- Endpoint: /sap/opu/odata/sap/API_PRODUCT_SRV
- Description: Full CRUD operations on product master data
- Replaces: direct access to MARA, MAKT, MARC, MARD tables
- Compliance: Mandatory replacement under v4/2026 for material master access

### I_Material (CDS View)
- Status: Released
- Type: Released CDS View
- Description: Read-only view exposing material master data
- Recommended for: analytical and reporting scenarios

### API_MATERIAL_STOCK_SRV
- Status: Released
- Description: Stock-related material data
- Compliance: Compliant with v4/2026

For material master data access, use the released API_MATERIAL_STOCK_SRV
or the CDS view I_Material. The API_PRODUCT_SRV provides full CRUD
operations on product master data including the fields previously
accessed via the MARA table.

## Business Partner (formerly Customer/Vendor)

### BAPI_BUPA_CREATE_FROM_DATA
- Status: Released
- Description: Creates a business partner (customer or vendor role)
- Replaces: BAPI_CUSTOMER_CREATEFROMDATA1, BAPI_VENDOR_CREATE
- Compliance: Mandatory replacement under Business Partner approach

### API_BUSINESS_PARTNER (OData)
- Status: Released
- Endpoint: /sap/opu/odata/sap/API_BUSINESS_PARTNER
- Description: Full business partner CRUD via OData
- Recommended for: cloud-native business partner integration



