
## Попытка научить pytorch нормально произносить русские аббревиатуры.
```
АООТ|акционерное общество открытого типа
АОР|архив Октябрьской революции
АТД|административно-территориальное деление
АФ|архивный фонд
БД|база данных
БУ|бюджетное учреждение
ВАПП|Всероссийская ассоциация пролетарских писателей

=>

ААООООТ+э.|акционерное общество открытого типа
ААОО+эР.|архив Октябрьской революции
ААТэД+э.|административно-территориальное деление
АА+эФ.|архивный фонд
БэД+э.|база данных
БэУ.|бюджетное учреждение
ВэААПэП+э.|Всероссийская ассоциация пролетарских писателей
```
```
py textToWav.py --help
usage: textToWav.py [-h] [-f FROMCHAR] [-t TOCHAR] [-n] [-q] [-o OUTPUTFILE] inputFile

positional arguments:
  inputFile             input text file (utf-8 encoded), "-" - read from stdin

options:
  -h, --help            show this help message and exit
  -f FROMCHAR, --fromChar FROMCHAR
                        process input starting from specified char (default: 0)
  -t TOCHAR, --toChar TOCHAR
                        process input till specified char (default: text length)
  -n, --noWav           don't generate wav
  -q, --quiet           don't output modified text
  -o OUTPUTFILE, --outputFile OUTPUTFILE
                        output wav-file name (in current dir) (default: out.wav)
```
