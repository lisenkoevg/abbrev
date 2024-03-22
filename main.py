import os
import sys
import argparse
from vowelizeAbbr import vowelizeAbbr

parser = argparse.ArgumentParser()
parser.add_argument('filename')
parser.add_argument('-f', '--fromLine', help='process only first LINES from file', type=int, default=0)
parser.add_argument('-t', '--toLine', help='process only first LINES from file', type=int, default=None)
parser.add_argument('-n', '--dryRun', help='only show generated xml', action='store_true')
args = parser.parse_args()

lines = open(args.filename, encoding="utf8").readlines()[args.fromLine:args.toLine]

def entag(x):
  line = x.split('|')
  line[0] = vowelizeAbbr(line[0])
  line[0] = '<s>' + line[0].strip() + '</s>'
  line[1] = f'{line[1].strip()}'
  line = ' '.join(line)
  return f'{line.strip()}\n'

txt = ''.join(list(map(entag, lines))).strip()
ssml_text = f'<speak><prosody rate="fast">\n{txt}\n</prosody></speak>'
print(ssml_text)
print('{} lines'.format(len(lines)))
if (args.dryRun): exit(0)

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
speaker='xenia'

audio_paths = model.save_wav(ssml_text=ssml_text,
                             speaker=speaker,
                             audio_path='tmp/test.wav',
                             sample_rate=sample_rate)
