import sys
import os
import argparse

from isAbbr import isAbbr
from ruEnc import lowerLetters
from ruEnc import upperLetters
from ruEnc import lowerLettersCp1251
from ruEnc import upperLettersCp1251
from ruEnc import cp1251

parser = argparse.ArgumentParser()
parser.add_argument('filename')
parser.add_argument('-c', '--count', help='process only first COUNT characters from file', type=int, default=None)
parser.add_argument('-e', '--encoding', help='encoding of input file', choices=['utf8', 'cp1251'], default='utf8')
args = parser.parse_args()

if not os.path.isfile(args.filename):
  print(f'file {args.filename} not exists')
  exit(1)

mode = 'r' if args.encoding == 'utf8' else 'rb'
content = open(args.filename, mode=mode, encoding=args.encoding if args.encoding == 'utf8' else None).read()[0:args.count]

if args.encoding == 'utf8':
  letters = lowerLetters | upperLetters
  up = upperLetters
if args.encoding == 'cp1251':
  letters = lowerLettersCp1251 | upperLettersCp1251
  up = upperLettersCp1251


def scanFileContentAndExtractAbbreviations(content):
  abbreviations = set()
  counter = 0
  upperLettersCounter = 0
  curWord = []
  for ch in content:
    counter += 1
    code = ch
    if code in letters:
      if code in up: upperLettersCounter += 1
      curWord.append(ch)
    else:
      if isAbbr(upperLettersCounter, len(curWord)):
        if args.encoding == 'utf8':
          abbreviations.add(''.join(curWord))
        else:
          abbreviations.add(bytes(curWord))
      curWord = []
      upperLettersCounter = 0
  return (counter, abbreviations)

counter, abbreviations = scanFileContentAndExtractAbbreviations(content)

sys.stderr.write(f'Total letters: {counter}\n')
if args.encoding == 'utf8':
  lst = list(abbreviations)
else:
  lst = list(map((lambda x: cp1251.decode(x)[0]), abbreviations)) 

lst.sort()
print('\n'.join(lst))
