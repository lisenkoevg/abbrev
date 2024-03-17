arr=(
  layout
  # simple
  # simple2
  # table
  # lineprinter
  # raw
  # 'fixed 1'
  # 'linespacing 1'
  # clip
  # nodiag
)
file=8_spisok_sokr.pdf
# base=${file%.pdf}
# for p in "${arr[@]}"; do
#   pdftotext -nopgbrk -enc UTF-8 -$p $file - | dos2unix -q "${base}__$p.txt"
# done
# txt=${base}__layout.txt

pdftotext -nopgbrk -enc UTF-8 -layout $file - | dos2unix -O \
  | sed -E '1,2d; /^\s+[0-9]+\s*$/d; /^\s*$/d' \
  | awk -f join.awk | grep -P '^[А-Я]+  ' \
  | sed -E 's/^(\S+)\s+(.*)$/\1|\2/' > abbr.txt
