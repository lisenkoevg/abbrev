import os
import sys

lines = open('samples/abbr.txt', encoding='utf8').readlines()[30:40]

def vowelize(x):
  chars1 = 'БВГДПТ'
  chars2 = 'ЛМРСФ'
  chars3 = 'К'
  if chars1.find(x) >= 0:
    return x + '+э'
  elif chars2.find(x) >= 0:
    return 'э' + x
  elif chars3.find(x) >= 0:
    return x + 'а'
  else:
    return x

def f1(x):
  line = x.split('|')
  line[0] = ''.join(list(map((lambda x: f'{vowelize(x)}'), line[0])))
  line[0] = '<s>' + line[0].strip() + '</s>'
  line[1] = f'<prosody rate="x-fast">{line[1].strip()}</prosody>'
  line = ' '.join(line)
  return f'{line.strip()}\n'

lines = list(map(f1, lines))
# ssml_text = ''.join(lines).strip()

# ssml_text = open('samples/sample.txt', encoding='utf8').read()[0:int(sys.argv[1])]
ssml_text = 'Событие произошло 11 января 2020 года.'
ssml_text = f'<speak><prosody rate="x-fast">\n{ssml_text}\n</prosody></speak>'
print(ssml_text)
# exit(1)

import torch

device = torch.device('cpu')
torch.set_num_threads(4)
local_file = 'tmp/model.pt'

if not os.path.isfile(local_file):
    torch.hub.download_url_to_file('https://models.silero.ai/models/tts/ru/v4_ru.pt',
                                   local_file)  
model = torch.package.PackageImporter(local_file).load_pickle("tts_models", "model")
model.to(device)
sample_rate = 48000
speaker='aidar'

audio_paths = model.save_wav(ssml_text=ssml_text,
                             speaker=speaker,
                             audio_path='tmp/test.wav',
                             sample_rate=sample_rate)
