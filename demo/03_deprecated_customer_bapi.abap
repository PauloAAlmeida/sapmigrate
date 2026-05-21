*&---------------------------------------------------------------------*
*& Report Z_CREATE_CUSTOMER_LEGACY
*& Creates customer using deprecated BAPI (legacy Customer/Vendor)
*&---------------------------------------------------------------------*

REPORT z_create_customer_legacy.

DATA: ls_customerdata TYPE bapikna101,
      ls_address      TYPE bapiad1vl,
      ls_return       TYPE bapiret2,
      lv_customerno   TYPE bapikna101-customer.

ls_customerdata-acct_grp = 'KUNA'.
ls_address-name          = 'Cliente Teste'.
ls_address-city          = 'Rio de Janeiro'.

CALL FUNCTION 'BAPI_CUSTOMER_CREATEFROMDATA1'
  EXPORTING
    pi_customerdata = ls_customerdata
    pi_personaldata = ls_address
  IMPORTING
    customerno      = lv_customerno
    return          = ls_return.
