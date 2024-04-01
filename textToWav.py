import os
import sys
import io
import re
import json

abbrStoreFile = 'abbrStore.json'

def main():
   abbrStore = loadAbbrStore()
   if args.inputFile != '-':
      inputStream = open(args.inputFile, 'r', encoding='utf8')
   else:
      inputStream = io.TextIOWrapper(sys.stdin.buffer, encoding='utf8')

   abbrs, contentAsLetterList, contentAsWordList = extractAbbr(inputStream)
#    if args.debug:
#       print('{}\n'.format(content))
#       print('{}\n'.format(contentAsWordList))
#       for x in abbrs: print(x)
#       print()
   modifiedAbbr = modifyAbbr(abbrs)
   if args.debug:
      for x in modifiedAbbr: print(x)
      print()
   if args.context == None:
      modifiedContent = inlineModifiedAbbr(modifiedAbbr, contentAsLetterList)
   else:
      modifiedContent = inlineModifiedAbbrContext(modifiedAbbr, contentAsWordList)
   if not args.quiet:
      print(modifiedContent)
   if not args.noWav:
      generateWav(modifiedContent, args.outputFile)
   saveAbbrStore(abbrStore, modifiedAbbr)

def loadAbbrStore():
   result = dict()
   if os.path.isfile(abbrStoreFile):
      result = json.loads(open(abbrStoreFile, encoding='utf8').read())
   return result

def saveAbbrStore(abbrStore, modifiedAbbr):
   modified = False
   for x in modifiedAbbr:
      if x['abbr'] in abbrStore: continue
      abbrStore[x['abbr']] = x['abbr_'] + ' | ' + str(x['pymorph'])
      modified = True
   if modified:
      j = json.dumps(abbrStore, sort_keys=True, ensure_ascii=False, indent=2)
      open(abbrStoreFile, mode='w', encoding='utf8').write(j)

def extractAbbr(inputStream):
   result = []
   contentAsLetterList = []
   contentAsWordList = []
   pos = 0
   posWord = 0
   upperLettersCounter = 0
   curWord = []
   isEnd = False
   for line in inputStream:
      if isEnd: break
      for ch in line:
         if not args.fromChar == None and pos < int(args.fromChar or 0): pos += 1; continue
         if not args.toChar == None and pos == int(args.toChar or 0): isEnd = True; break
         contentAsLetterList.append(ch)
         if ch.isalpha():
            if ch.isupper(): upperLettersCounter += 1
            curWord.append(ch)
         else:
            if len(curWord) > 0:
               strWord = ''.join(curWord)
               if isAbbr(''.join(curWord), upperLettersCounter):
                  result.append({
                     'abbr': strWord,
                     'pos': pos - len(curWord),
                     'posWord': posWord
                  })
               contentAsWordList.append(strWord)
               posWord += 1
               curWord = []
               upperLettersCounter = 0
         pos += 1
   if len(curWord) > 0:
      if isAbbr(''.join(curWord), upperLettersCounter):
         result.append({
            'abbr': ''.join(curWord),
            'pos': pos - len(curWord),
            'posWord': posWord
         })
      contentAsWordList.append(''.join(curWord))
   return result, contentAsLetterList, contentAsWordList

def modifyAbbr(abbrList):
   for ab in abbrList:
      ab['abbr_'] = vowelizeAbbr(ab['abbr'])
      ab['isPymorphyAbbr'], ab['pymorph'] = isPymorphyAbbr(ab['abbr'])
   return abbrList

def inlineModifiedAbbr(modifiedAbbreviations, contentAsLetterList):
   shift = 0
   for ab in modifiedAbbreviations:
      if args.excludeWithPymorphy and not ab['isPymorphyAbbr']: continue
      startPos = ab['pos'] + shift
      endPos = ab['pos'] + len(ab['abbr']) + shift
      contentAsLetterList[startPos:endPos] = list(ab['abbr_'])
      shift += (len(ab['abbr_']) - len(ab['abbr']))
   return ''.join(contentAsLetterList)

def inlineModifiedAbbrContext(modifiedAbbreviations, contentAsWordList):
   result = []
   uniq = set()
   if args.excludeWithPymorphy:
      modifiedAbbreviations = [x for x in modifiedAbbreviations if x['isPymorphyAbbr']]
   for ab in modifiedAbbreviations:
      p = ab['posWord']
      contentAsWordList[p] = ab['abbr_']
   for ab in modifiedAbbreviations:
      if not args.context == None:
         if (ab['abbr'] in uniq): continue
         uniq.add(ab['abbr'])
      p = ab['posWord']
      s = ab['abbr'] + ' ' if args.noWav else ''
      result.extend([s + '...'
         + ' '.join(contentAsWordList[p - args.context:p + args.context + 1])
         + '...\n'])
   return ''.join(result)

def generateWav(text, audio_path):
   if len(text.strip()) == 0: return
   import wave
   import time
   ts = str(time.time_ns())
   fragments = splitTextIntoFragments(text)

   if not args.quiet: print("generating {} ({} chunks)...".format(audio_path, len(fragments)), end='', flush=True)
   for (i, text) in enumerate(fragments):
      f = audio_path.replace('.wav', f'_{i}_{ts}.wav')
      generateWav_(text, f)
      if not args.quiet: print(f' {i+1}', end='', flush=True)
   if not args.quiet: print()
   # combine wav-chunks
   wav = wave.open(audio_path, 'wb')
   for (i, text) in enumerate(fragments):
      f = audio_path.replace('.wav', f'_{i}_{ts}.wav')
      w = wave.open(f, 'rb')
      params = w.getparams()
      frames = w.readframes(params.nframes)
      if i == 0: wav.setparams(params)
      wav.writeframes(frames)
      w.close()
      os.remove(f)
   wav.close()


def generateWav_(text, audio_path):
   import torch
   device = torch.device('cpu')
   torch.set_num_threads(4)
   local_file = 'model.pt'

   if not os.path.isfile(local_file):
      torch.hub.download_url_to_file('https://models.silero.ai/models/tts/ru/v4_ru.pt',
                                      local_file)
   model = torch.package.PackageImporter(local_file).load_pickle("tts_models", "model")
   model.to(device)
   sample_rate = 48000
   speaker='xenia'

   audio_paths = model.save_wav(
      text=text,
      speaker=speaker,
      audio_path=audio_path,
      sample_rate=sample_rate)

def isAbbr(abbr, upperLettersCounter):
   le = len(abbr)
   if le < 2: return False
   if re.match('[A-Z]', abbr): return False
   if le <= 4:
      return upperLettersCounter == le
   else:
      return upperLettersCounter >= (le - 2)

import pymorphy3
morph = pymorphy3.MorphAnalyzer()
def isPymorphyAbbr(abbr):
   # Некоторую часть абрревиатур pymorphy3 не распознаёт (сравн.
   # tests\textToWav\krasn_vesna.out
   # tests\textToWav\krasn_vesna_Excluded_by_PyMorph.out)
   #
   # >>> pymorphy3.MorphAnalyzer().parse('СССР')[0].tag => OpencorporaTag('NOUN,inan,masc,Sgtm,Fixd,Abbr,Geox sing,gent')
   # >>> pymorphy3.MorphAnalyzer().parse('ГДР')[0].tag => OpencorporaTag('NOUN,inan,femn,Fixd,Geox sing,gent')
   mo = morph.parse(abbr)[0]
   return ('Abbr' in mo.tag or 'Geox' in mo.tag, mo.tag)

def vowelizeAbbr(abbr):
   result = ''
   VOWELS = 'АЕИОУЭЮЯ'
   vowel = f'[{VOWELS}]'
   consonant = f'[^{VOWELS}]'

   abbrLen = len(abbr)
   maOnlyConsonants = re.search(f'^{consonant}+$', abbr)
   maThreeOrMoreConsonants = not maOnlyConsonants and re.search(f'{consonant}{{3,}}', abbr)
   maVowelsInside = not maThreeOrMoreConsonants and re.search(f'^{consonant}.*{vowel}.*{consonant}$', abbr)
   maVowelConsonantInterchanges = not maVowelsInside and re.search(f'^(({consonant}{vowel})+|({vowel}{consonant})+)$', abbr)
   maVowelFromTheSide = not maVowelConsonantInterchanges and re.search(f'^{vowel}|{vowel}$', abbr)
#    print(abbr, f'\n{maOnlyConsonants=}\n{maThreeOrMoreConsonants=}\n{maVowelsInside=}\n{maVowelConsonantInterchanges=}\n{maVowelFromTheSide=}')
   if maOnlyConsonants: # print('Только согласные', maOnlyConsonants)
      result = vowelizeAbbrLetters(abbr)
   elif maThreeOrMoreConsonants: # print('Три и более согласных подряд')
      span = maThreeOrMoreConsonants.span()
      result = ''.join([
         abbr[0:span[0]],
         vowelizeAbbrLetters(abbr[span[0]:span[1]]),
         abbr[span[1]:]
      ])
   elif maVowelConsonantInterchanges: # print('Гласные чередуются с согласными')
      result = abbr
   elif maVowelsInside: # print('Гласные "внутри"')
      result = abbr
   elif maVowelFromTheSide: # print('Начинается или заканчивается с гласной')
      ma = re.search(f'{consonant}+', abbr)
      span = ma and ma.span()
      if span and span[1] - span[0] == 1:
         result = abbr
      else:
         result = vowelizeAbbrLetters(abbr)
   return result

def vowelizeAbbrLetters(abbr):
   postE = 'БВГДЖЗПТЦЧ'
   preE = 'ЛМНРСФ'
   postA = 'К'

   abbrLen = len(abbr)
   li = []
   i = 0
   while i < len(abbr):
      isLast = (i == abbrLen - 1)
      x = abbr[i]
      stress = '+' if isLast else ''
      if postE.find(x) >= 0: x = f'{x}{stress}э'
      elif preE.find(x) >= 0: x = f'{stress}э{x}'
      elif postA.find(x) >= 0: x = f'{x}{stress}' + 'а' * 1
      li.append(x)
      i += 1
   return ''.join(li)

MAX_TEXT_LENGTH_FOR_TORCH = 800
def splitTextIntoFragments(text):
   SPLIT_CHAR = ' '
   low = 0
   high = MAX_TEXT_LENGTH_FOR_TORCH
   splitPositions = []
   prevPos = 0
   while True:
      if high > len(text):
         splitPositions.append((prevPos, None))
         break
      pos = text.rfind(SPLIT_CHAR, low, high)
      if pos != -1:
         splitPositions.append((prevPos, pos))
         prevPos = pos + 1
         low = pos + 1
         high = low + MAX_TEXT_LENGTH_FOR_TORCH
      else:
         low += MAX_TEXT_LENGTH_FOR_TORCH
         high += MAX_TEXT_LENGTH_FOR_TORCH
   result = []
   for (l, h) in splitPositions:
      result.append(text[l:h])
   return result

def handleOpts():
   global MAX_TEXT_LENGTH_FOR_TORCH
   global args
   import argparse
   parser = argparse.ArgumentParser()
   parser.add_argument('inputFile', help='input text file (utf-8 encoded), "-" - read from stdin')
   parser.add_argument('-f', '--fromChar', metavar='N', help='process input starting from char N', type=int, default=None)
   parser.add_argument('-t', '--toChar', metavar='N', help='process input till char N (default: text length)', type=int, default=None)
   parser.add_argument('-c', '--context', metavar='N', help='process only N words before and after each abbreviation', type=int, default=None)
   parser.add_argument('-m', '--maxChunkLength', metavar='N',
      help=f'max text chunk length for "torch" input (default {MAX_TEXT_LENGTH_FOR_TORCH})', type=int, default=MAX_TEXT_LENGTH_FOR_TORCH)
   group = parser.add_mutually_exclusive_group()
   group.add_argument('-n', '--noWav', help='don\'t generate wav', action='store_true')
   group.add_argument('-q', '--quiet', help='don\'t output modified text', action='store_true')
   parser.add_argument('-d', '--debug', help='show intermediate results', action='store_true')
   parser.add_argument('-p', '--excludeWithPymorphy', help='filter out abbreviation candidates with pymorphy3 if "Abbr" and "Geox" tags is False', action='store_true')
   parser.add_argument('-o', '--outputFile', metavar="wavFile", help='output wav-file name (dir must exists if specified) (default: out.wav)', default="out.wav")
   args = parser.parse_args()
   if 0 == len(range(int(args.fromChar or 0), int(args.toChar or sys.maxsize))):
      print('incorrect --fromChar/--toChar')
      exit(1)
   if 10 <= args.maxChunkLength <= 2000:
      MAX_TEXT_LENGTH_FOR_TORCH = args.maxChunkLength
   else:
      print('incorrect --maxChunkLength, try 10...2000')
      exit(1)

handleOpts()
main()

