*&---------------------------------------------------------------------*
*& Report Z_CREATE_PO_CLEAN
*& Creates purchase order using published BAPI
*&---------------------------------------------------------------------*
REPORT z_create_po_clean.

DATA: ls_poheader  TYPE bapimepoheader,
      ls_poheaderx TYPE bapimepoheaderx,
      lt_poitems   TYPE TABLE OF bapimepoitem,
      lt_return    TYPE TABLE OF bapiret2.

ls_poheader-comp_code  = 'BR01'.
ls_poheader-doc_type   = 'NB'.
ls_poheader-vendor     = '0000100000'.
ls_poheaderx-comp_code = 'X'.
ls_poheaderx-doc_type  = 'X'.
ls_poheaderx-vendor    = 'X'.

CALL FUNCTION 'BAPI_PO_CREATE1'
  EXPORTING
    poheader  = ls_poheader
    poheaderx = ls_poheaderx
  TABLES
    return    = lt_return
    poitem    = lt_poitems.

COMMIT WORK.
