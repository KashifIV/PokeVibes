from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

gauth = GoogleAuth()           
drive = GoogleDrive(gauth)  

folder = '1BkBvtP643A9SEUk7k0TVE3RjZ3OutY3K'

def upload_file(file_path): 
  gfile = drive.CreateFile({'parents': [{'id': folder}]})
  gfile.SetContentFile(file_path)
  gfile.Upload() 


dir = './favourites/' 
import os 
for file in os.listdir(dir): 
  upload_file(dir + file)