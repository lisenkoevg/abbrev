def isAbbr(upperLetterCount, length):
  if length <= 4: return upperLetterCount == length
  else: return upperLetterCount >= (length - 2)
