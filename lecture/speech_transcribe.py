import speech_recognition as sr
import os
r = sr.Recognizer()

orig_file = 'transcript.wav'
num_files = 16 #get length of file in minutes

os.system('ffmpeg -i "transcript.wav" -f segment -segment_time 60 -c copy transcript_%03d.wav')

audio_head = orig_file[:-4] + '_'

output_file = open("transcript.txt", "w")

for i in range(num_files):
	audio = audio_head + str(i).zfill(3) + '.wav'
	with sr.AudioFile(audio) as source:
	   audio = r.record(source)
	try:
	   text = r.recognize_google(audio)
	   output_file.write(text)
	   output_file.write(" ")
	except Exception as e:
	   print (e)
	print("file " + str(i) + " done")
output_file.close()