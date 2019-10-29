import speech_recognition as sr
import os
from os import path
import sys

filename = str(sys.argv[1])
if ('.wav' not in filename):
	print("FILENAME MUST BE WAV")
	sys.exit()

os.system("ffmpeg -i {0} -f segment -segment_time 60 -c copy transcript_%03d.wav".format(filename))

r = sr.Recognizer()

numFiles = 0
while True:
	audio = "transcript_{0}.wav".format(str(numFiles).zfill(3))
	if not path.exists(audio):
		break
	else:
		numFiles+=1

block = ""
print("Translating...")
i = 0
for i in range(numFiles):
	audio = "transcript_{0}.wav".format(str(i).zfill(3))

	with sr.AudioFile(audio) as source:
	    audio = r.record(source)
	    # print ('Done!')
	try:
	    text = r.recognize_google(audio)
	    print('{0}/15 done'.format(i+1))
	    block += text
	    
	except Exception as e:
	    print (e)

with open('output.txt','w') as outfile:
	outfile.write(block)