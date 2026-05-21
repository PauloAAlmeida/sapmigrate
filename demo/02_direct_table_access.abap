REPORT z_legacy_material_report.

DATA: lt_mara TYPE TABLE OF mara,
      lt_marc TYPE TABLE OF marc.

" Direct access to MARA — prohibited by v4/2026
SELECT matnr mtart matkl mbrsh
  FROM mara
  INTO CORRESPONDING FIELDS OF TABLE lt_mara
  WHERE mtart = 'FERT'.

" Direct access to MARC — same violation
SELECT matnr werks dispo
  FROM marc
  INTO CORRESPONDING FIELDS OF TABLE lt_marc
  FOR ALL ENTRIES IN lt_mara
  WHERE matnr = lt_mara-matnr.
