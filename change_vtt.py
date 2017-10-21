def change_vtt(insert_file_path):
	print ('run change_vtt.py from :'+'./static'+insert_file_path)
	f = open('./static'+insert_file_path)
	text = f.read()
	f.close()
	f = open('./static'+insert_file_path, 'w')
	f.write("WEBVTT\n\n")
	f.write(text)
	f.close()