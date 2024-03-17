#!/bin/bash

trap 'RC=1' ERR
for testInput in tests/*.in; do
  testOutput=${testInput%.*}.out
  testActual=${testInput%.*}_actual.out
  py extractAbbr.py $testInput -1 | iconv -f CP1251 -t UTF-8 > $testActual
  diff -qN $testOutput $testActual && {
    echo Test $testInput ok
    rm -f $testActual
   } || {
     echo Test $testInput failed
     false
   }
done
[ -z "$RC" ] && nircmd beep 3000 50
