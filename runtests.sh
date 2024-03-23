#!/bin/bash

function main() {
  echo _BIGTEST=$_BIGTEST _TIME=$_TIME
  bigTest=5000000

  [ -n "$_TIME" ] && _time=time

  RC=
  testProg textToWav 'py $prog.py -n $testInput -c 3'
#   [ -z "$RC" ] && beep 3000 50

#   RC=
  testProg extractAbbr 'py $prog.py $testInput $enc'
  [ -z "$RC" ] && beep 3000 50
}

function testProg() {
  prog=$1
  make -sB -C c CFLAGS=-s
  for testInput in tests/$prog/*.in; do
    echo $testInput | grep -qF "/." && continue
    let inputSize=$(stat -c %s $testInput)
    [ $inputSize -gt $bigTest ] && [ -z "$_BIGTEST" ] && continue
    testOutput=${testInput%.*}.out
    testActual=${testInput%.*}_actual.out
    cp1251=$(echo $testInput | grep -o cp1251)
    if [ -n "$cp1251" ]; then
      enc='--encoding cp1251'
      iconv=
    else
      enc=
      iconv=' | iconv -f CP1251 -t UTF-8'
    fi
    evalStr="$_time $2 $iconv"
    eval "$evalStr" | dos2unix > $testActual
    diff -qN $testOutput $testActual && {
      echo Python test $testInput ok
      rm -f $testActual
    } || {
      echo Python test $testInput failed
      RC=1
    }
    py -c 'print("=" * 50)'

    [ -e ./c/$prog.exe ] && [ -n "$enc" ] && {
      eval $_time './c/$prog.exe < '$testInput'| dos2unix > '${testActual}_c
      diff -qN $testOutput ${testActual}_c && {
        echo C test $testInput ok
        rm -f ${testActual}_c
      } || {
        echo C test $testInput failed
        RC=1
      }
      py -c 'print("=" * 50)'
    }
  done
  make -s -C c clean
}

main
