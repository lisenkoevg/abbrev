import os
import sys
import io

def main():
   global args
   if args.inputFile != '-':
      content = open(args.inputFile, 'r', encoding='utf8').read()
   else:
      input_stream = io.TextIOWrapper(sys.stdin.buffer, encoding='utf8')
      content = input_stream.read()
   content = content[args.fromChar:args.toChar].strip().replace('\n', '.\n')

   abbrs, contentAsLetterList, contentAsWordList = extractAbbr(content)
   if args.debug:
      print('{}\n'.format(content))
      print('{}\n'.format(contentAsWordList))
      for x in abbrs: print(x)
      print()
   modifiedAbbr = modifyAbbr(abbrs)
   if args.debug:
      for x in modifiedAbbr: print(x)
      print()
   if args.context == 0:
      modifiedContent = inlineModifiedAbbr(modifiedAbbr, contentAsLetterList)
   else:
      modifiedContent = inlineModifiedAbbrContext(modifiedAbbr, contentAsWordList, args.context)
   if not args.quiet:
      print(modifiedContent)
   if not args.noWav:
      generateWav(modifiedContent, args.outputFile)

def extractAbbr(content):
   result = []
   contentAsLetterList = []
   contentAsWordList = []
   pos = 0
   posWord = 0
   upperLettersCounter = 0
   curWord = []
   for ch in content:
      contentAsLetterList.append(ch)
      if ch.isalpha():
         if ch.isupper(): upperLettersCounter += 1
         curWord.append(ch)
      else:
         if len(curWord) > 0:
            if isAbbr(''.join(curWord), upperLettersCounter):
               result.append({
                  'abbr': ''.join(curWord),
                  'pos': pos - len(curWord),
                  'posWord': posWord
               })
            contentAsWordList.append(''.join(curWord))
            posWord += 1
            curWord = []
            upperLettersCounter = 0
      pos += 1
   return result, contentAsLetterList, contentAsWordList

def modifyAbbr(abbrList):
   for ab in abbrList:
      ab['abbr_'] = vowelizeAbbr(ab['abbr'])
#       ab['isPymorphyAbbr'] = isPymorphyAbbr(ab['abbr'])
   return abbrList

def inlineModifiedAbbr(modifiedAbbreviations, contentAsLetterList):
   shift = 0
   for ab in modifiedAbbreviations:
      startPos = ab['pos'] + shift
      endPos = ab['pos'] + len(ab['abbr']) + shift
      contentAsLetterList[startPos:endPos] = list(ab['abbr_'])
      shift += (len(ab['abbr_']) - len(ab['abbr']))
   return ''.join(contentAsLetterList)

def inlineModifiedAbbrContext(modifiedAbbreviations, contentAsWordList, contextWordNum):
   global args
   result = []
   for ab in modifiedAbbreviations:
      p = ab['posWord']
      contentAsWordList[p] = ab['abbr_']
   for ab in modifiedAbbreviations:
      p = ab['posWord']
      s = ab['abbr'] + ' ' if args.noWav else ''
      result.extend([s + '...'
         + ' '.join(contentAsWordList[p - contextWordNum:p + contextWordNum + 1])
         + '...\n'])
   return ''.join(result)

def generateWav(text, audio_path):
   if len(text.strip()) == 0: return
   import wave
   import time
   ts = str(time.time_ns())
   fragments = splitTextIntoFragments(text)

   print("generating {} ({} chunks)...".format(audio_path, len(fragments)), end='', flush=True)
   for (i, text) in enumerate(fragments):
      f = audio_path.replace('.wav', f'_{i}_{ts}.wav')
      generateWav_(text, f)
      print(f' {i+1}', end='', flush=True)
   print()
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
   import re
   le = len(abbr)
   if le < 2: return False
   if re.match('[A-Z]', abbr): return False
   if le <= 4:
      return upperLettersCounter == le and isPymorphyAbbr(abbr)
   else:
      return upperLettersCounter >= (le - 2) and isPymorphyAbbr(abbr)

import pymorphy3
morph = pymorphy3.MorphAnalyzer()
def isPymorphyAbbr(abbr):
   global args
   if not args.excludeWithPymorphy:
      return True
   # Некоторую часть абрревиатур pymorphy3 не распознаёт (сравн.
   # tests\textToWav\krasn_vesna.out
   # tests\textToWav\krasn_vesna_Excluded_by_PyMorph.out)
   #
   # >>> pymorphy3.MorphAnalyzer().parse('СССР')[0].tag => OpencorporaTag('NOUN,inan,masc,Sgtm,Fixd,Abbr,Geox sing,gent')
   # >>> pymorphy3.MorphAnalyzer().parse('ГДР')[0].tag => OpencorporaTag('NOUN,inan,femn,Fixd,Geox sing,gent')
   mo = morph.parse(abbr)[0]
   return 'Abbr' in mo.tag or 'Geox' in mo.tag

cache = {}
def vowelizeAbbr(abbr):
   if abbr in cache: return cache[abbr]
   abbrLen = len(abbr)
   li = []
   i = 0
   while i < len(abbr):
      li.append(vowelizeAbbrLetter(abbr[i], i == len(abbr) - 1))
      i += 1
   cache[abbr] = ''.join(li)
   return cache[abbr]

def vowelizeAbbrLetter(x, isLast):
   postE = 'БВГДПТЦЧ'
   preE = 'ЛМНРСФ'
   postA = 'К'
   twice = 'ОАИ'
   stress = '+' if isLast else ''
   if postE.find(x) >= 0: x = f'{x}{stress}э'
   elif preE.find(x) >= 0: x = f'{stress}э{x}'
   elif postA.find(x) >= 0: x = f'{x}{stress}' + 'а' * 1
   elif twice.find(x) >= 0: x = f'{x}{stress}{x.upper() * 1}'
   return x + ('.' if isLast else '')

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

args = 0
def handleOpts():
   global MAX_TEXT_LENGTH_FOR_TORCH
   global args
   import argparse
   parser = argparse.ArgumentParser()
   parser.add_argument('inputFile', help='input text file (utf-8 encoded), "-" - read from stdin')
   parser.add_argument('-f', '--fromChar', metavar='N', help='process input starting from char N (default: 0)', type=int, default=0)
   parser.add_argument('-t', '--toChar', metavar='N', help='process input till char N (default: text length)', type=int, default=None)
   parser.add_argument('-c', '--context', metavar='N', help='process only N words before and after each abbreviation', type=int, default=0)
   parser.add_argument('-m', '--maxChunkLength', metavar='N',
      help=f'max text chunk length for "torch" input (default {MAX_TEXT_LENGTH_FOR_TORCH})', type=int, default=MAX_TEXT_LENGTH_FOR_TORCH)
   group = parser.add_mutually_exclusive_group()
   group.add_argument('-n', '--noWav', help='don\'t generate wav', action='store_true')
   group.add_argument('-q', '--quiet', help='don\'t output modified text', action='store_true')
   parser.add_argument('-d', '--debug', help='show intermediate results', action='store_true')
   parser.add_argument('--excludeWithPymorphy', help='filter out abbreviation candidate with pymorphy3 "Abbr" and "Geox" tags False', action='store_true')
   parser.add_argument('-o', '--outputFile', metavar="wavFile", help='output wav-file name (in current dir) (default: out.wav)', default="out.wav")
   args = parser.parse_args()
   if args.fromChar < 0 or int(args.toChar or 0) < 0 or args.fromChar > int(args.toChar or 0):
      print('incorrect --fromChar/--toChar')
      exit(1)
   if 10 <= args.maxChunkLength <= 2000:
      MAX_TEXT_LENGTH_FOR_TORCH = args.maxChunkLength
   else:
      print('incorrect --maxChunkLength, try 10...2000')
      exit(1)

handleOpts()
main()

