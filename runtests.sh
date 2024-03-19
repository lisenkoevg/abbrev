#!/bin/bash

RC=
for testInput in tests/*.in; do
  echo $testInput | grep -qF "/." && continue
  testOutput=${testInput%.*}.out
  testActual=${testInput%.*}_actual.out
  cp1251=$(echo $testInput | grep -o cp1251)
  enc=${cp1251:+--encoding cp1251}
  iconv="${enc:-| iconv -f CP1251 -t UTF-8}"

  time eval py extractAbbr.py $testInput $enc $iconv > $testActual
  diff -qN $testOutput $testActual && {
    echo Python test $testInput ok
    rm -f $testActual
  } || {
    echo Python test $testInput failed
    RC=1
  }
  py -c 'print("=" * 40)'

  [ -n "$enc" ] && {
    time eval './c/extractAbbr.exe < '$testInput'| sort -u > '${testActual}_c
    diff -qN $testOutput ${testActual}_c && {
      echo C test $testInput ok
      rm -f ${testActual}_c
    } || {
      echo C test $testInput failed
      RC=1
    }
    py -c 'print("=" * 40)'
  }
done
[ -z "$RC" ] && nircmd beep 3000 50
