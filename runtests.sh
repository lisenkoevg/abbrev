#!/bin/bash

echo _BIGTEST=$_BIGTEST _TIME=$_TIME
bigTest=5000000

RC=
make -sB -C c CFLAGS=-s
for testInput in tests/*.in; do
  echo $testInput | grep -qF "/." && continue
  let inputSize=$(stat -c %s $testInput)
  [ $inputSize -gt $bigTest ] && [ -z "$_BIGTEST" ] && continue
  testOutput=${testInput%.*}.out
  testActual=${testInput%.*}_actual.out
  cp1251=$(echo $testInput | grep -o cp1251)
  enc=${cp1251:+--encoding cp1251}
  iconv="${enc:-| iconv -f CP1251 -t UTF-8}"
  [ -n "$_TIME" ] && _time=time

  eval $_time py extractAbbr.py $testInput $enc $iconv | dos2unix > $testActual
  diff -qN $testOutput $testActual && {
    echo Python test $testInput ok
    rm -f $testActual
  } || {
    echo Python test $testInput failed
    RC=1
  }
  py -c 'print("=" * 40)'

  [ -n "$enc" ] && {
    eval $_time './c/extractAbbr.exe < '$testInput'| dos2unix > '${testActual}_c
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
make -s -C c clean
[ -z "$RC" ] && beep.sh 3000 50
