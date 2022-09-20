from datetime import date
from youtube.youtube_api import get_vote_ratio
from datetime import datetime, timedelta, timezone
import shutil
import asyncio
import os
from time import sleep 
import pygame
import pyautogui

dir_path = os.path.dirname(os.path.realpath(__file__))
ready_path = '{}/ready_music/'.format(dir_path)
used_path = '{}/used_music/'.format(dir_path)
favourite_path = '{}/favourites/'.format(dir_path)
learning_path = '{}/learning/'.format(dir_path)

pygame.mixer.init()
pygame.init()
# display = pygame.display.set_mode((800, 600))

def load_available_songs(): 
  files = [] 
  for file in os.listdir(ready_path): 
    if '.wav' in file: 
      files.append(os.path.join(ready_path, file))
  return files 


class Fader(object):
  instances = []
  def __init__(self, fname):
    super(Fader, self).__init__()
    self.fname =fname
    self.sound = pygame.mixer.Sound(fname)
    self.increment = 0.01 # tweak for speed of effect!!
    self.next_vol = 1 # fade to 100 on start
    Fader.instances.append(self)

  def fade_to(self, new_vol):
    # you could change the increment here based on something..
    self.next_vol = new_vol

  @classmethod
  def update(cls):
    for inst in cls.instances:
      curr_volume = inst.sound.get_volume()
      # print inst, curr_volume, inst.next_vol
      if inst.next_vol > curr_volume:
        inst.sound.set_volume(curr_volume + inst.increment)
      elif inst.next_vol < curr_volume:
        inst.sound.set_volume(curr_volume - inst.increment)

async def count_votes(file_name):
  end = datetime.now(timezone.utc)
  start = end - timedelta(minutes=2)
  print('Counting Votes for', file_name.split('/')[-1])
  try: 
    voted_ratio, L_ratio = get_vote_ratio(start, end)
    print(voted_ratio)
    print(L_ratio)
    if voted_ratio > 0.25:
      print('Favouriting', file_name.split('/')[-1])
      shutil.copy2(file_name, favourite_path)
      shutil.copy2(file_name.split('.')[0] + '.mid', favourite_path)
      pyautogui.hotkey('f1')
    elif L_ratio > 0.25:
      print('Learning', file_name.split('/')[-1])
      shutil.copy2(file_name, learning_path)
      shutil.copy2(file_name.split('.')[0] + '.mid', learning_path)
      pyautogui.hotkey('f3')
    else: 
      pyautogui.hotkey('f2')
  except: 
    print('Failed to get ratio.')
  
  os.remove(file_name)
  os.remove(file_name.split('.')[0] + '.mid')

try: 
  for _ in range(200): 
    songs = load_available_songs()
    print('Found', str(len(songs)), 'songs.')
    previous_song = None
    for song in songs:
      if previous_song != None:
        sleep(120)
        previous_song.fade_to(0)
        asyncio.run(count_votes(previous_song.fname))
      audio = Fader(song)
      audio.sound.play()
      print('Playing', song.split('/')[-1])
      audio.sound.set_volume(0)
      audio.fade_to(1)
      for _ in range(100):
        Fader.update()
      if previous_song != None: 
        previous_song.sound.stop()
      audio.sound.set_volume(1)
      previous_song = audio
except KeyboardInterrupt: 
  print('Done Playing!')
  pygame.mixer.pause()