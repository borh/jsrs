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

ROOT_PATH = 'jsrs/media/'

# 発音評価02 is different
# JP_EXPERIMENT_1: native speakers
# SE Data/n... -> native speakers
# SE Data/s... -> foreign speakers (students)

def audio_files(path):
    '''Generator returning full_path, basename, and extension of all audio files under given path.'''
    for root, dirs, files in os.walk(path, followlinks=True):
        for name in files:
            (basename, extension) = os.path.splitext(name)
            full_path = os.path.join(root, name)
            if re.match(r'\.(mp3|wav)', extension):
                relpath = os.path.relpath(full_path, os.path.abspath(ROOT_PATH))
                recording_set, reader, _ = Path(full_path).parts[-3:]
                sentence = int(''.join(n for n in basename if n.isdigit()))
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


def generate_fixtures(root_path):
    '''Generates and writes fixtures to json file for later loading.'''
    #preprocess(root_path)
    with open('audio-files-fixtures.json', 'w') as f:
        f.write(json.dumps([{'model': 'audio.Audio',
                             'fields': {'path': relpath, 'group': recording_set, 'reader': '{}-{}'.format(recording_set, reader), 'sentence': sentence}} for (path, _, extension, relpath, recording_set, reader, sentence) in audio_files(root_path) if extension == '.mp3'], ensure_ascii=False))

if __name__ == '__main__':
    generate_fixtures(os.path.abspath(ROOT_PATH))
