#!/usr/bin/env python3
'''
Audio file paths must be formatted according to the following convention:

/path/to/$recording_set/$reader/$sentence.mp3
-- or --
/path/to/$recording_set/$reader-$sentence.mp3

Where $recording_set signifies the grouping of readers and sentences and $reader signifies the reader of the sentence $sentence.
Note that the combination of $recording_set, $reader and $sentence must be unique for all sets of audio files.

Modify the ROOT_PATH as necessary below and run this script with:
python3 generate_fixtures.py
'''

import os
from pathlib import Path
import subprocess
import re
import json
from collections import defaultdict

ROOT_PATH = 'jsrs/media/'
FILE_VARIANT = False

# 発音評価02 is different
# JP_EXPERIMENT_1: native speakers
# SE Data/n... -> native speakers
# SE Data/s... -> foreign speakers (students)
# Pilot/ follows $reader-$sentence.mp3 pattern

def audio_files(path, reader_filter=None, sentence_filter=None, sentence_exclusion_filter=None):
    '''Generator returning full_path, basename, and extension of all audio files under given path.'''
    for root, dirs, files in os.walk(path, followlinks=True):
        for name in files:
            basename, extension = os.path.splitext(name)
            full_path = os.path.join(root, name)
            if re.match(r'\.(mp3|wav)', extension):
                relpath = os.path.relpath(full_path, os.path.abspath(ROOT_PATH))
                if FILE_VARIANT:
                    _, recording_set, _ = Path(full_path).parts[-3:]
                    reader, sentence_string = basename.split('-')
                    if reader_filter and reader not in reader_filter:
                        continue
                    sentence = int(''.join(n for n in sentence_string if n.isdigit())) # remove non-digits
                    if sentence_filter and sentence not in sentence_filter:
                        continue
                    if sentence in sentence_exclusion_filter[reader]:
                        continue
                    yield((full_path, basename, extension, relpath, recording_set, reader, sentence))
                else:
                    recording_set, reader, _ = Path(full_path).parts[-3:]
                    if reader_filter and reader not in reader_filter:
                        continue
                    sentence = int(''.join(n for n in basename if n.isdigit())) # remove non-digits
                    if sentence_filter and sentence not in sentence_filter:
                        continue
                    if sentence in sentence_exclusion_filter[reader]:
                        continue
                    yield((full_path, basename, extension, relpath, recording_set, reader, sentence))


def preprocess(root_path):
    '''Transcodes any missing mp3 files from their wav source and performs normalization on all mp3 files.'''
    for (full_path, basename, extension, _, _, _, _) in audio_files(os.path.abspath(root_path)):
        if extension == '.wav':
            mp3_version = os.path.join(os.path.dirname(full_path), basename) + '.mp3'
            if not os.path.exists(mp3_version):
                print('Transcoding {} to {}'.format(full_path, mp3_version))
                subprocess.run(['ffmpeg', '-i', full_path, '-qscale:a', '2', mp3_version])
    for (full_path, _, extension, _, _, _, _) in audio_files(os.path.abspath(ROOT_PATH)):
        if extension == '.mp3':
            print('Normalizing {}'.format(full_path))
            subprocess.run(['mp3gain', '-e', '-r', '-p', '-c', full_path])

import pandas as pd
import numpy as np
import math
def sentence_fixtures(fn='データID.xlsx'):
    '''Generates sentence fixtures from file'''
    sentences = pd.read_excel(fn, sheetname=0, names=['number', 'order', 'text'])
    for pk, row in enumerate(sentences.itertuples()):
        yield {'model': 'audio.Sentence',
               'pk': pk+1,
               'fields': {'number': np.asscalar(row.number),
                          'order': np.asscalar(row.order),
                          'set': int(math.floor((np.asscalar(row.order)-1)/5)) + 1,
                          'text': row.text}}

def reader_fixtures(fn='データID.xlsx'):
    '''Generates reader fixtures from file'''
    sentences = pd.read_excel(fn, sheetname=1, names=['old_name', 'gender', 'name', 'disabled'])
    for pk, row in enumerate(sentences.itertuples()):
        d = False
        if row.disabled == 0:
            d = True
        ns = True
        if row.name[1] == '1':
            ns = False
        yield {'model': 'audio.Reader',
               'pk': pk+1,
               'fields': {'name': row.name, 'gender': row.gender, 'native_speaker': ns, 'disabled': d}}

def generate_fixtures(root_path):
    '''Generates and writes fixtures to json file for later loading.'''
    #preprocess(root_path)
    #print([a for a in audio_files(root_path)])

    sentence_number2pk = {sentence['fields']['number']: sentence['pk'] for sentence in sentence_fixtures()}
    sentence_filter = set(sentence_number2pk.keys())

    reader_name2pk = {reader['fields']['name']: reader['pk'] for reader in reader_fixtures()}
    reader_filter = set(reader_name2pk.keys())

    sentence_exclusion_df = pd.read_excel('データID.xlsx', sheetname=2, names=['old_name', 'sentence_id', 'new_name'])
    sentence_exclusion_filter = defaultdict(set)
    for row in sentence_exclusion_df.itertuples():
        sentence_exclusion_filter[row.new_name].add( np.asscalar(row.sentence_id))

    with open('audio-sentence-fixtures.json', 'w') as f:
        f.write(json.dumps([sentence for sentence in sentence_fixtures()], ensure_ascii=False))

    with open('audio-reader-fixtures.json', 'w') as f:
        f.write(json.dumps([reader for reader in reader_fixtures()], ensure_ascii=False))

    with open('audio-audio-fixtures.json', 'w') as f:
        f.write(json.dumps([{'model': 'audio.Audio',
                             'fields': {'path': relpath,
                                        #'group': recording_set,
                                        'reader': reader_name2pk[reader],
                                        'sentence': sentence_number2pk[sentence]}}
                            for (path, _, extension, relpath, recording_set, reader, sentence) in audio_files(root_path, reader_filter, sentence_filter, sentence_exclusion_filter) if extension == '.mp3'], ensure_ascii=False))

if __name__ == '__main__':
    generate_fixtures(os.path.abspath(ROOT_PATH))
