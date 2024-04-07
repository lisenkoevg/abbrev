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
$ py textToWav/textToWav.py --help
usage: textToWav.py [-h] [-f N] [-t N] [-c N] [-m N] [-n | -q] [-d] [-p]
                    [-o wavFile]
                    inputFile

positional arguments:
  inputFile             input text file (utf-8 encoded), "-" - read from stdin

options:
  -h, --help            show this help message and exit
  -f N, --fromChar N    process input starting from char N
  -t N, --toChar N      process input till char N (default: text length)
  -c N, --context N     process only N words before and after each
                        abbreviation
  -m N, --maxChunkLength N
                        max text chunk length for "torch" input (default 800)
  -n, --noWav           don't generate wav
  -q, --quiet           don't output modified text
  -d, --debug           show intermediate results
  -p, --excludeWithPymorphy
                        filter out abbreviation candidates with pymorphy3 if
                        "Abbr" and "Geox" tags is False
  -o wavFile, --outputFile wavFile
                        output wav-file name (dir must exists if specified)
                        (default: out.wav)

```
