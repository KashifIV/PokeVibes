from mixing.MGS.song import Song
from mido import MidiFile
from mixing.assign_program import get_program
import os 
import numpy as np 
import subprocess 


dir_path = os.path.dirname(os.path.realpath(__file__))
sound_file = os.path.join(dir_path, 'Pokemon_DPPt_GM_SoundfontFix.sf2')

def to_wav(path, output_path): 
  wav_command = [
    'fluidsynth', sound_file, '-F','{}.wav'.format(output_path.split('.')[0]), path
  ]
  proc = subprocess.run(wav_command)
  return proc.stdout == 0

def is_sticky(file_path): 
  max_length = 24*5
  song = Song(MidiFile(file_path))
  pr = song.to_pianoroll()

  track_index = None
  current_streak = 0
  for x in range(pr.tracks[0].pianoroll.shape[0]):
    notes = [] 
    for track in pr.tracks: 
      notes.append(np.sum(track.pianoroll[x]))
    notes = np.array(notes)

    index = np.argmin(notes)
    if notes[index] == np.sum(notes): 
      if track_index == index:
        current_streak +=1
        if current_streak >= max_length: 
          return True 
      else: 
        track_index = index 
        current_streak = 1
    else: 
      track_index = None 
      current_streak = 0
  return False 



def mix(file_path, output_dir): 
  song = Song(MidiFile(file_path))
  midi = get_program(song)
  path = '{}/mixed_music/'.format(dir_path) + file_path.split('/')[-1]
  midi.write(path)
  if not is_sticky(path): 
    to_wav(path, output_dir + file_path.split('/')[-1])
  os.remove(path)
