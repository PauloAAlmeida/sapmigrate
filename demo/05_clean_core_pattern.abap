REPORT z_btp_wrapper_call.

DATA: lo_http_client TYPE REF TO if_web_http_client,
      lv_response    TYPE string.

" Clean Core pattern: calls published OData wrapper on BTP
" instead of accessing MARA table directly
TRY.
    lo_http_client = cl_web_http_client_manager=>create_by_http_destination(
      i_destination = cl_http_destination_provider=>create_by_url(
        'https://api.s4hana.cloud/v1/API_PRODUCT_SRV/A_Product'
      )
    ).

    lo_http_client->get_http_request( )->set_header_fields( VALUE #(
      ( name = 'Accept' value = 'application/json' )
    ) ).

    lv_response = lo_http_client->execute(
      i_method = if_web_http_client=>get
    )->get_text( ).

  CATCH cx_web_http_client_error INTO DATA(lx_error).
    " tratamento
ENDTRY.

