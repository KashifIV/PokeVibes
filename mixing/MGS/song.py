from time import sleep
from mido import MidiFile
import pretty_midi
import pypianoroll
import mido 
from mixing.MGS.track import Track
from mixing.MGS.midi_instruments import instrument_map
import numpy as np 

class Song: 
  def __init__(self, file: MidiFile):
    self.file = file
    self.tracks = self.get_tracks(file)
    self.title = file.filename.split('/')[-1]

  def get_tracks(self, file: MidiFile):
    tempo = self.get_tempo()
    tracks = [Track(track, file.ticks_per_beat, tempo) for track in file.tracks]
    return tracks
  
  def get_tempo(self): 
    for msg in self.file: 
      if msg.type == 'set_tempo': 
        return msg.dict()['tempo']
    return 500000

  def __str__(self): 
    return self.title
  
  def play(self, channel=None): 

    with mido.open_output('IAC Driver Bus 1') as port: 
      for message in self.file.play():
        sleep(message.time)
        if not message.is_meta:
          if channel == None or message.type != 'note_on' or channel == message.dict()['channel']:
            port.send(message)
  
  def to_pianoroll(self): 
    target_midi = pretty_midi.PrettyMIDI(self.file.filename)
    return pypianoroll.from_pretty_midi(target_midi)

  def get_melody_track(self) -> Track: 
    max_notes = 0
    ans = None
    for track in self.tracks:
      if len(track.notes) > max_notes:
        max_notes = len(track.notes)
        ans = track
        # has_piano = False 
        # for instrument in track.instruments: 
        #   if 'Piano' in instrument:
        #     has_piano = True
        # if has_piano or ans == None: 
        #   ans = track 
        #   max_notes = len(track.notes)

    return ans 
  
  def get_melody_orc_matrix(self, s, n, h):
    if len(self.tracks) < h+1: 
      return {}, {}

    melody = self.get_melody_track()

    orchestra = []
    for track in self.tracks:
      if len(orchestra) == h: 
        break 

      if track != melody and len(track.intervaled_notes) > 64:
        orchestra.append(track)
    
    if (len(orchestra) < h): 
      return {}, {}

    melody_meta, melody_notes, _ = melody.get_sparse_range_matrix(s, n, is_time=True)
    
    orchestra_meta = []
    orchestra_notes = []
    target_meta = []
    target_notes = []
    for track in orchestra: 
      prev_notes = track.get_last_n(s, n)
      if (len(prev_notes) > 0):
        meta, notes, _  = track.sparse_matrix(prev_notes)
      else: 
        meta = [] 
        notes = []
      if len(meta) < n: 
        delta = n - len(meta)
        meta = [[0.1]*3]*delta + meta 
        notes = [[0.1]*128]*delta + notes
      
      ans_meta, ans_notes, _ = track.get_sparse_range_matrix(s, n, is_time=True)
      if len(ans_meta) < n: 
        delta = n - len(ans_meta)
        ans_meta = ans_meta + [[0.1]*3]*delta
        ans_notes = ans_notes + [[0.1]*128]*delta
      
      target_meta.append(ans_meta)
      target_notes.append(ans_notes)
      orchestra_meta.append(meta)
      orchestra_notes.append(notes)

    if len(orchestra_meta) != h: 
      print(len(orchestra_meta))
    
    return {
        'melody_meta': np.asarray(melody_meta).astype('float32'),
        'melody_notes': np.asarray(melody_notes).astype('float32'),  
        'orchestra_meta': np.asarray(orchestra_meta).astype('float32'), 
        'orchestra_notes': np.asarray(orchestra_notes).astype('float32'), 
    }, {
      'target_meta': np.asarray(target_meta).astype('float32'),
      'target_notes': np.asarray(target_notes).astype('float32'),
    }
