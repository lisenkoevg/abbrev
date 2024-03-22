lowerLetters = set(range(ord('а'), ord('я') + 1)) | { ord('ё') }
lowerLetters = set(map((lambda x: chr(x)), lowerLetters))

upperLetters = set(range(ord('А'), ord('Я') + 1)) | { ord('Ё') }
upperLetters = set(map((lambda x: chr(x)), upperLetters))
