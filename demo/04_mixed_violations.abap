*&---------------------------------------------------------------------*
*& Report Z_ORDER_PROCESSING
*& Order processing — mixes compliant and non-compliant patterns
*&---------------------------------------------------------------------*

REPORT z_order_processing.

DATA: lt_vbak     TYPE TABLE OF vbak,         " acesso interno
      ls_salesord TYPE bapisdhead1,            " BAPI publicada
      ls_return   TYPE bapiret2.

" Violação 1: SELECT direto em VBAK
SELECT vbeln auart kunnr
  FROM vbak
  INTO CORRESPONDING FIELDS OF TABLE lt_vbak
  WHERE erdat >= sy-datum.

" OK: cria pedido de venda via BAPI publicada
CALL FUNCTION 'BAPI_SALESORDER_CREATEFROMDAT2'
  EXPORTING
    order_header_in = ls_salesord
  IMPORTING
    return          = ls_return.

" Violação 2: chamada RFC interna (Z*)
CALL FUNCTION 'Z_INTERNAL_PRICE_CALC'
  EXPORTING
    iv_matnr = 'ABC123'
  IMPORTING
    ev_price = DATA(lv_price).
