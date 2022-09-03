from generation.generate import generate, clean_workspace, dump_midi
from mixing.mix import mix
import os 
from concurrent.futures import ThreadPoolExecutor, Future
from threading import current_thread
from time import sleep

dir_path = os.path.dirname(os.path.realpath(__file__))
dump_midi()

def job(): 
  number = current_thread().getName()
  clean_workspace(number)
  files = generate(number, 8)
  for file in files: 
    mix(file, '{}/ready_music/'.format(dir_path))


def fill_queue():
  with ThreadPoolExecutor(max_workers=3) as pool:
    for x in range(3): 
      pool.submit(job)

def ready_songs():
  count = 0
  for item in os.listdir('{}/ready_music/'.format(dir_path)):
    count += 1
  return count 

try: 
  while True:
    num_songs = ready_songs()
    if num_songs < 90:
      fill_queue()
    else: 
      print('Waiting: Queue at', num_songs, 'songs.')
      sleep(1000)
    # dump_midi()
except KeyboardInterrupt: 
  print('Stopping Music Generation')
