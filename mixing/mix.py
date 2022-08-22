from mixing.MGS.song import Song
from mido import MidiFile
from mixing.assign_program import get_program
import os 
import subprocess 


dir_path = os.path.dirname(os.path.realpath(__file__))
sound_file = os.path.join(dir_path, 'Pokemon_DPPt_GM_SoundfontFix.sf2')

def to_wav(path, output_path): 
  wav_command = [
    'fluidsynth', sound_file, '-F','{}.wav'.format(output_path.split('.')[0]), path
  ]
  proc = subprocess.run(wav_command)
  return proc.stdout == 0 

def mix(file_path, output_dir): 
  song = Song(MidiFile(file_path))
  midi = get_program(song)
  path = '{}/mixed_music/'.format(dir_path) + file_path.split('/')[-1]
  midi.write(path)
  to_wav(path, output_dir + file_path.split('/')[-1])
  os.remove(path)
