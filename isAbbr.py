def isAbbr(upperLettersCounter, allLettesCount):
   if upperLettersCounter < 2: return False
   if allLettesCount <= 4: return upperLettersCounter == allLettesCount
   else: return upperLettersCounter >= (allLettesCount - 2)
