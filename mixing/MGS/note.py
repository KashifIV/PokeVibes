from mido import Message
class Note: 
  def __init__(self, note_data: Message):
    properties = str(note_data).split(' ')
    self.channel = properties[1].split('=')[1]
    self.value = properties[2].split('=')[1]
    self.velocity = properties[3].split('=')[1]
    self.time = properties[4].split('=')[1]
    
  def __str__(self): 
    return self.value + ' at ' + self.time