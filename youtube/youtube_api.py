from itertools import count
import os
import json 
from datetime import datetime
from dateutil import parser
from time import sleep

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

dir_path = os.path.dirname(os.path.realpath(__file__))
f = open('{}/youtube_keys.json'.format(dir_path))
keys = json.load(f)

DEVELOPER_KEY = keys['apiKey']
CHAT_ID = keys['chatId']

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
api_service_name = "youtube"
api_version = "v3"

youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey = DEVELOPER_KEY)

def get_vote_ratio(start_time, end_time):
  request = youtube.liveChatMessages().list(
      liveChatId=CHAT_ID,
      part="snippet",
      maxResults = 500,
    )
  response = request.execute()

  chats = response['items']
  authors = set()
  voted_authors = set()
  L_authors = set()

  while len(chats) != 0: 
    for chat in chats: 
      publish_time = parser.parse(chat['snippet']['publishedAt'])

      if publish_time.time()< start_time.time():
        continue
      
      if publish_time.time() < end_time.time():
        author = chat['snippet']['authorChannelId']
        if not author in authors:
          authors.add(author)
        if '!!!' in chat['snippet']['displayMessage'] and not author in voted_authors:
          voted_authors.add(author)
        if 'LLL' in chat['snippet']['displayMessage'] and not author in L_authors:
          L_authors.add(author) 

    if response['pageInfo']['totalResults'] > 500:
      sleep(0.5)
      request = youtube.liveChatMessages().list(
        liveChatId=CHAT_ID,
        part="snippet",
        pageToken=response['nextPageToken'],
        maxResults = 500,
      )
      response = request.execute()
      chats = response['items']
    else: 
      chats = []

  if len(authors) == 0: 
    return 0,0

  return (len(voted_authors)/len(authors), len(L_authors)/len(authors))
      
  