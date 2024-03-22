cache = {}

def vovelizeAbbr(word):
  if word in cache: return cache[word]
  cache[word] = ''.join(list(map((lambda x: vowelizeAbbrLetter(x)), word))) 
  return cache[word]

def vowelizeAbbrLetter(x):
  postE = 'БВГДПТЦЧ'
  preE = 'ЛМНРСФ'
  postA = 'К'
  twice = 'ОАИ'
  if postE.find(x) >= 0: x = x + 'э'
  elif preE.find(x) >= 0: x = 'э' + x
  elif postA.find(x) >= 0: x = x + 'А' * 2
  elif twice.find(x) >= 0: x = x + x.upper() * 2
  return x + ','
