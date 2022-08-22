from email import message
from tracemalloc import start
from mido import MidiTrack, tick2second
from mixing.MGS.note import Note 
from mixing.MGS.midi_instruments import instrument_map

class Track: 
  def __init__(self, track: MidiTrack, ticks_per_beat, tempo):
    self.name = track.name
    self.tempo = tempo
    self.ticks_per_beat = ticks_per_beat
    self.track_data = track
    self.instruments = []
    self.notes = []
    self.length = 1
    self.process_messages()
    self.intervaled_notes = self.interval_notes()


  def get_instrument(self): 
    for msg in self.track_data: 
      if msg.type == 'program_change': 
        return msg.dict()['program']
    return 1

  
  def process_messages(self): 
    current_instrument = self.get_instrument()
    tempo = self.tempo
    instruments = set()
    total_time = 0
    for msg in self.track_data: 
      if msg.type == 'note_on' or msg.type == 'note_off':
        values = msg.dict()
        message_type = msg.type
        if msg.type == 'note_on' and values['velocity'] == 0: 
          message_type = 'note_off'
        total_time += values['time']
        #total_time += tick2second(values['time'],self.ticks_per_beat, tempo)
        self.notes.append({
          'type': message_type, 
          'note': values['note'],
          'velocity': values['velocity'],
          'time': values['time'],
          'absolute_time': total_time,
          'instrument': current_instrument
        })
      elif msg.type == 'program_change': 
        current_instrument = msg.dict()['program']
        instruments.add(instrument_map[msg.dict()['program']])
      elif msg.type == 'set_tempo': 
        tempo = msg.dict()['tempo']
    self.instruments = list(instruments)
    self.length = total_time

  def get_range(self, start_time, num_notes):
    values = []
    for note in self.intervaled_notes: 
      if note['absolute_time'] > start_time: 
        values.append(note)
        if len(values) == num_notes: 
          return values 
    return values

  def get_range_matrix(self, start_time, n): 
    notes = self.get_range(start_time, n)
    ans = [] 
    for x in notes: 
      ans.append([x['note'], x['velocity'], x['instrument'], x['time'], x['length']])
    return ans 
  


  def get_sparse_range_matrix(self, s, n, is_time=False):
    if is_time: 
      notes = self.get_range(s, n)
    else: 
      notes = self.intervaled_notes[s:n]
    if len(notes) < n: 
      return [], [], []
    
    return self.sparse_matrix(notes)
  
  def sparse_matrix(self, notes): 

    notes_ans = [] 
    meta_ans = []
    for x in notes: 
      meta_ans.append([x['velocity'], x['time'], x['length']])
      
      note = [0]*128
      note[x['note']] = 1 
      notes_ans.append(note)

    program = [0]*128
    program[notes[0]['instrument']] = 1

    return meta_ans, notes_ans, program


  def get_last_n(self, s, n): 
    history = []
    for x in self.intervaled_notes: 
      if x['absolute_time'] >= s: 
        return history[-n:]
      else: 
        history.append(x)
    return history[-n:]

  def interval_notes(self):
    intervaled_notes = []
    last_note_on = {}
    for note in self.notes: 
      if note['type'] == 'note_on': 
        last_note_on[note['note']] = note
      elif note['type'] == 'note_off' and note['note'] in last_note_on:
        original_note = last_note_on[note['note']]
        original_note['length'] = note['absolute_time'] - original_note['absolute_time']
        intervaled_notes.append(original_note)
        last_note_on.pop(note['note'])
    return intervaled_notes


  def __str__(self):
    return self.name