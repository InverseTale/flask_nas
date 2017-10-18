def change_vtt(file_name):
	f = open('/Users/hyun/Documents/workspace/flask_nas/static/uploads/test10/'+filename)
	text = f.read()
	f.close()

	f = open('/Users/hyun/Documents/workspace/flask_nas/static/uploads/test10/'+filename, 'w')
	f.write("WEBVTT\n\n")
	f.write(text)
	f.close()