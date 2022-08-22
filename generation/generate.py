import os 
import subprocess
import pypianoroll
import pretty_midi
import numpy as np 
import shutil 
import random
import string


dir_path = os.path.dirname(os.path.realpath(__file__))

def sample(job_number, samples):
  sample_generation = [
    'music_vae_generate',
    '--config=hierdec-trio_16bar',
    '--checkpoint_file={}/model.tar.gz'.format(dir_path),
    '--mode=sample',
    '--num_outputs={}'.format(samples),
    '--output_dir={}/sample/workspace{}/'.format(dir_path, str(job_number)),
  ]
  proc = subprocess.run(sample_generation)
  return proc.stdout == 0 


def interpolate(a, b, job_number, batch_number):
  interp_generation = [
    'music_vae_generate',
    '--config=hierdec-trio_16bar',
    '--checkpoint_file={}/model.tar.gz'.format(dir_path),
    '--mode=interpolate',
    '--num_outputs=4',
    '--input_midi_1={}'.format(a),
    '--input_midi_2={}'.format(b),
    '--output_dir={}/interpolate/workspace{}/song{}'.format(dir_path, str(job_number), str(batch_number))
  ]
  proc = subprocess.run(interp_generation)
  return proc.stdout == 0


def mix_tracks(workspace):
  parts = []
  for file in os.listdir(workspace): 
    # part = file.split('_')[-1].split('-')[1]
    midi = pretty_midi.PrettyMIDI(os.path.join(workspace,file))
    parts.append(pypianoroll.from_pretty_midi(midi))
  if len(parts) == 0: 
    return None
  mt = parts[0]
  for i in range(len(mt.tracks)): 
    combined_track = parts[0].tracks[i].pianoroll
    for part in parts[1:]: 
      combined_track = np.append(combined_track, part.tracks[i].pianoroll, axis = 0)
    mt.tracks[i].pianoroll = combined_track
  
  return mt 


def clean_workspace(job_number): 
  sample_dir = '{}/sample/workspace{}/'.format(dir_path, str(job_number))
  if os.path.exists(sample_dir):
    shutil.rmtree(sample_dir)

  interp_dir = '{}/interpolate/workspace{}/'.format(dir_path, job_number)
  if os.path.exists(interp_dir):
    shutil.rmtree(interp_dir)

def dump_midi(): 
  path = dir_path + '/music/'
  for file in os.listdir(path): 
    os.remove(path + file)

def generate(job_number, batch_size):
  print('Sampling Latent Space...')
  sample(job_number, batch_size*2)

  sample_dir = '{}/sample/workspace{}/'.format(dir_path, str(job_number))
  sample_files = []
  for file in os.listdir(sample_dir): 
    sample_files.append(os.path.join(sample_dir, file))
  
  print(sample_files)
  print('Interpolating Samples...')
  for i in range(0, len(sample_files), 2): 
    interpolate(sample_files[i], sample_files[i+1], job_number, i//2)

  print('Mixing Tracks...')
  interp_dir = '{}/interpolate/workspace{}/'.format(dir_path, job_number)
  letters = string.ascii_lowercase
  files = []
  for folder in os.listdir(interp_dir):
    mt = mix_tracks(os.path.join(interp_dir, folder))
    if mt != None: 
      midi = pypianoroll.to_pretty_midi(mt)
      file_path = dir_path + '/music/' + ''.join(random.choice(letters) for i in range(7)) + '.mid'
      midi.write(file_path)
      files.append(file_path)
  return files
