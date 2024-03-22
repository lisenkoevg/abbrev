import codecs
from ruLetters import lowerLetters
from ruLetters import upperLetters

utf8 = codecs.lookup('utf8')
cp1251 = codecs.lookup('cp1251')

lowerLettersCp1251 = set() 
upperLettersCp1251 = set() 

for ch in upperLetters:
  upperLettersCp1251.add(cp1251.encode(ch)[0][0])
for ch in lowerLetters:
  lowerLettersCp1251.add(cp1251.encode(ch)[0][0])

'''
def printLetters(lettersSet, printHeader=False):
  cp866 = codecs.lookup('cp866')
  koi8r = codecs.lookup('koi8-r')
  fmtHead = '%-5s %4s %8s %6s %6s'
  fmtLine = '%-5s %2X%2X %6X %6X %6X'
  if printHeader:
    print(fmtHead % ('char', 'utf8', 'cp1251', 'cp866', 'koi8-r'))
    print('=' * 34) 
  for ch in sorted(list(lettersSet)):
    tmp1 = utf8.encode(ch)[0]
    tmp2 = cp1251.encode(ch)[0][0]
    tmp3 = cp866.encode(ch)[0][0]
    tmp4 = koi8r.encode(ch)[0][0]
    print(fmtLine % (ch, tmp1[0], tmp1[1], tmp2, tmp3, tmp4))

printLetters(upperLetters, True)
printLetters(lowerLetters)
'''
