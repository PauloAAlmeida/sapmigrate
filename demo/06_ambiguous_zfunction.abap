REPORT z_custom_logic.

DATA: lv_result TYPE i.

" Custom Z function — no public documentation
CALL FUNCTION 'Z_CUSTOM_BUSINESS_RULE'
  EXPORTING
    iv_param1 = 100
    iv_param2 = 'X'
  IMPORTING
    ev_result = lv_result.
