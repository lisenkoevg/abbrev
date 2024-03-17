import sys
import os
import re

inputFile = sys.argv[1]
if not os.path.isfile(inputFile):
  print(f'file {inputFile} not exists')
  exit(1)

content = open(inputFile, encoding='utf8').read()[0:int(sys.argv[2])]

lowerLetters = set(range(ord('а'), ord('я') + 1)) | { ord('ё') }
lowerLetters = set(map((lambda x: chr(x)), lowerLetters))
upperLetters = set(range(ord('А'), ord('Я') + 1)) | { ord('Ё') }
upperLetters = set(map((lambda x: chr(x)), upperLetters))
letters = lowerLetters | upperLetters

abbreviations = set()

def isAbbr(upperLetterCount, length):
  if length <= 4: return upperLetterCount == length
  else: return upperLetterCount >= (length - 2)

counter = 0
upperLetterCounter = 0
curWord = []
for ch in content:
  counter += 1
  code = ch
  if code in letters:
    if code in upperLetters: upperLetterCounter += 1
    curWord += ch
  else:
    if upperLetterCounter >= 2 and isAbbr(upperLetterCounter, len(curWord)):
        abbreviations.add(''.join(curWord))
    curWord = []
    upperLetterCounter = 0

# print(f'Total letters: {counter}')
lst = list(abbreviations)
lst.sort()
print('\n'.join(lst))

