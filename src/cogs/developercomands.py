import os

path = '../../'
dest = '../songs/that.mp3'
for file in os.listdir(path):
    if file.endswith(".mp3"):
        print(path + ' includes ' + file)
        if file.endswith(".mp3"):
            print(file)
            os.rename(path + file, dest)