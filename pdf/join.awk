BEGIN {
  cur = ""
}
/^\S/ {
  if (cur != "")
    print cur
  cur = $0
}
/^\s/ {
  gsub(/^\s+|\s+$/, "")
  cur = cur " " $0
}
END {
  print cur
}
