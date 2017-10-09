from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug import secure_filename
import os
app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSTIONS'] = set(['mp4','avi'])

def allowed_file(filename):
	return '.' in filename and \
		filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSTIONS']


@app.route('/')
def index():
	return render_template('index.html')

@app.route('/upload', methods = ['POST'])
def upload():
	uploaded_files = request.files.getlist("file[]")
	filenames = []

	if request.method == 'POST':
		for file in uploaded_files:
			if file and allowed_file(file.filename):
				filename = secure_filename(file.filename)
				file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
				filenames.append(filename)
			else:
				error_text = 'you can upload video extention'
				return render_template('index.html', error_text=error_text)
		return render_template('upload.html', filenames=filenames)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
	return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
	app.run(debug=True)