import sys
import os
import re
import requests
import json

TMPDIR = 'tmp'
SLOVARI = {
   '27': 'Словарь собственных имён русского языка. Агеенко',
   '71': 'Русский орфографический словарь. Под ред. Лопатина',
}
SLOVAR_PRIORITY = '27', '71'
SEARCH_LINK_BASE = 'https://gramota.ru/poisk'
SEARCH_LINK = '{0}?{1}&{2}&{3}&query='.format(
   SEARCH_LINK_BASE,
   'mode=slovari',  # поиск в словарях
   'simple=1',      # точное совпадение
   '&'.join(['dicts[]=' + x for x in SLOVARI])
)
SLOVAR_FILE_NAME = 'slovari_gramota.ru.json'

verbose = False
def main(abbr, v=False):
   global verbose
   verbose = v
   if not os.path.isdir(TMPDIR):
      os.mkdir(TMPDIR)

   slovar = loadSlovar()
   if not abbr in slovar:
      pronunciation = parseAbbr(abbr)
      if verbose: print('%s => [%s]' % (abbr, pronunciation))

      saveAbbr(abbr, pronunciation, slovar)
      saveSlovar(slovar)
   for id in SLOVAR_PRIORITY:
      if id in slovar[abbr] and slovar[abbr][id]:
         return slovar[abbr][id]
   else:
      return ''

def loadSlovar():
   result = dict()
   if os.path.isfile(SLOVAR_FILE_NAME):
      result = json.loads(open(SLOVAR_FILE_NAME, encoding='utf8').read())
   return result

def saveSlovar(slovar):
   if not hasattr(saveSlovar, 'changed'): return
   if verbose: print('saving slovar')
   j = json.dumps(slovar, sort_keys=True, ensure_ascii=False, indent=2)
   open(SLOVAR_FILE_NAME, mode='w', encoding='utf8').write(j)
   delattr(saveSlovar, 'changed')

def saveAbbr(abbr, pronunciation, SLOVAR):
   if not abbr in SLOVAR:
      SLOVAR[abbr] = pronunciation
      if verbose: print('adding attrib saveSlovar.changed')
      saveSlovar.changed = True

def writeTmp(base, suf, content):
   spl = '_' if suf else ''
   open(TMPDIR + '/' + base + spl + suf, 'w', encoding='utf8').write(content)

def loadTmp(tmpFile):
   if os.path.isfile(TMPDIR + '/' + tmpFile):
      return open(TMPDIR + '/' + tmpFile, encoding='utf8').read()

'''
<div class="dictionary-part ...">
   <div class="items common  order-1 ">
      <div class="item" data-dict-id="71">
         ...
         <div class="description highlightable">
            <b>СССР</b> [эс-эс-эс-<span class='hl_red'>э</span>р] — Союз Советских Социалиастических Республик (1922—1991)
or          <b>ФРГ [фэ-эр-г<span class='hl_red'>э</span>]</b>
or          <p><span class='title'>МВД</span> [эмвэд<span class='accent'>э</span>]
         </div>
       </div>
      <div class="item" data-dict-id="27">
         ...
         <div class="description highlightable">
            ...
         </div>
      </div>
      ...
   </div>
</div>
<div class="mt-40px  pb-40px"></div>
<div class="meta-part order-3">
'''
def parseAbbr(abbr):
   result = { x: '' for x in SLOVARI }
   tmpFile = abbr + '_' + ','.join(list(SLOVARI))
   htmlStr = loadTmp(tmpFile)
   if not htmlStr:
      link = SEARCH_LINK + abbr
      print('request {}'.format(link), flush=True)
      r = requests.get(link)
      htmlStr = r.text
      writeTmp(tmpFile, '', htmlStr)
   ma = re.search(
      '(<div class="dictionary-part.*(?=<div class="meta-part))', htmlStr, re.S)
   if not ma:
      if verbose: print('div dictionary-part not found')
      ma = re.search('<div class="nothing-found">', htmlStr)
      if ma:
         if verbose: print('abbr not found in selected dictionaries')
         return result
   dictionary = ma.group(1).strip()
   writeTmp(tmpFile, 'dictionary-part', dictionary)

   for id in SLOVARI:
      ma = re.search('<div class="item" data-dict-id="' + id + '">.*?'
         + '<div class="description[^>]*?>(.*?)</div>', dictionary, re.S)
      if not ma:
         if verbose: print('div description not found for slovar ' + id)
         continue
      item = ma.group(1).strip()
      writeTmp(tmpFile, 'description' + id, item)
      variants = [
         '<b>(.*)</b>\s+\[(.*?)\]',
         '<b>(.*)\s+\[(.*?)\]</b>',
         '<span class=.title.>(.*?)\s*</span>.*\[(.*?)\]'
      ]
      for v in variants:
         ma = re.search(v, item)
         if ma:
            abbrRes, pronunciation = ma.group(1, 2)
            if abbrRes == abbr:
               pronunciation = re.sub('<span.*?>', '+', pronunciation)
               pronunciation = re.sub('</span>|-', '', pronunciation)
               result[id] = pronunciation
               break
      else:
         if verbose: print('abbreviation parse error for slovar ' + id)

   return result
print(main(sys.argv[1], v=True))
