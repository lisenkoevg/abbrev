#/bin/bash

trap 'RC=1' ERR
make -sB
for inFile in tests/*.in; do
  outFile=${inFile%.in}.out
  outActual=${inFile%.in}_actual.out
  eval "./linkedList_test.exe < $inFile > $outActual"
  diff -qN $outFile $outActual > /dev/null && {
    echo Test $inFile passed...
    rm $outActual
  } || {
    echo Test $inFile FAILED...
  }
done
make -s clean
[ -z "$RC" ] && type nircmd > /dev/null && nircmd beep 2000 50
