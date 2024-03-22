import os
import sys
import io

def main(args):
   if args.inputFile != '-':
      content = open(args.inputFile, 'r', encoding='utf8').read()
   else:
      input_stream = io.TextIOWrapper(sys.stdin.buffer, encoding='utf8')
      content = input_stream.read()
   content = content[args.fromChar:args.toChar].strip().replace('\n', '.\n')

   abbrs, contentAsLetterList = extractAbbr(content)
   modifiedAbbr = modifyAbbr(abbrs)
#    if args.debug or args.noWav:
#       print(modifiedAbbr)
   modifiedContent = inlineModifiedAbbr(contentAsLetterList, modifiedAbbr)
   if not args.quiet:
      print(modifiedContent, '\n')
   if not args.noWav:
      generateWav(modifiedContent, args.outputFile)

def extractAbbr(content):
   result = []
   contentAsLetterList = []
   pos = 0
   upperLettersCounter = 0
   curWord = []
   for ch in content:
      contentAsLetterList.append(ch)
      pos += 1
      if ch.isalpha():
         if ch.isupper(): upperLettersCounter += 1
         curWord.append(ch)
      else:
         if isAbbr(upperLettersCounter, len(curWord)):
            result.append({ 'abbr': ''.join(curWord), 'pos': pos - 1 - len(curWord) })
         curWord = []
         upperLettersCounter = 0
   return result, contentAsLetterList

def modifyAbbr(abbrList):
   for ab in abbrList:
      ab['abbr_'] = vowelizeAbbr(ab['abbr'])
      ab['isPymorphyAbbr'] = isPymorphyAbbr(ab['abbr'])
   return abbrList

def inlineModifiedAbbr(contentAsLetterList, modifiedAbbreviations):
   result = []
   shift = 0
   for ab in modifiedAbbreviations:
      startPos = ab['pos'] + shift
      endPos = ab['pos'] + len(ab['abbr']) + shift
      contentAsLetterList[startPos:endPos] = list(ab['abbr_'])
      shift += (len(ab['abbr_']) - len(ab['abbr']))
   return ''.join(contentAsLetterList)
   
def generateWav(text, audio_path):
   print("generating {}...".format(audio_path))
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

   audio_paths = model.save_wav(text=text,
                                 speaker=speaker,
                                 audio_path=audio_path,
                                 sample_rate=sample_rate)

def isAbbr(upperLettersCounter, allLettesCount):
   if upperLettersCounter < 2: return False 
   if allLettesCount <= 4: return upperLettersCounter == allLettesCount
   else: return upperLettersCounter >= (allLettesCount - 2)

import pymorphy3
morph = pymorphy3.MorphAnalyzer()
def isPymorphyAbbr(abbr):
   mo = morph.parse(abbr)[0]
   return 'Abbr' in mo.tag

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

def handleOpts():
   import argparse
   parser = argparse.ArgumentParser()
   parser.add_argument('inputFile', help='input text file (utf-8 encoded), "-" - read from stdin')
   parser.add_argument('-f', '--fromChar', help='process input starting from specified char (default: 0)', type=int, default=0)
   parser.add_argument('-t', '--toChar', help='process input till specified char (default: text length)', type=int, default=None)
   parser.add_argument('-n', '--noWav', help='don\'t generate wav', action='store_true')
   parser.add_argument('-q', '--quiet', help='don\'t output modified text', action='store_true')
#    parser.add_argument('-d', '--debug', help='show found abbreviations and modified text', action='store_true')
   parser.add_argument('-o', '--outputFile', help='output wav-file name (default: out.wav)', default="out.wav")
   args = parser.parse_args()
   if args.noWav and args.quiet:
      parser.print_help()
      exit(1)
   return args

main(handleOpts())

