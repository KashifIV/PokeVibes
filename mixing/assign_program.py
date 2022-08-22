from mixing.MGS.song import Song 
from mixing.MGS.midi_instruments import instrument_map
import pypianoroll
import tensorflow as tf
from tensorflow import keras
import numpy as np 
import os 

dir_path = os.path.dirname(os.path.realpath(__file__))
model = keras.models.load_model('{}/instrument_assignment.h5'.format(dir_path))

def get_program(song: Song): 
  pr = song.to_pianoroll()
  for i in range(len(song.tracks)-1):
    meta, notes, _ = song.tracks[i].get_sparse_range_matrix(0, 64)
    print(len(meta))
    if len(meta) < 64:
      delta = 64 - len(meta)
      meta += [[0]*3]*delta
      notes +=  [[0]*128]*delta

    value = model.predict([np.asarray([meta]).astype('float32'), np.asarray([notes]).astype('float32')])
    program = value.argmax()
    pr.tracks[i].program = program 

  generated_pm = pypianoroll.to_pretty_midi(pr)
  return generated_pm