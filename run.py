# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug import secure_filename
from config import *
import os
app = Flask(__name__, static_url_path="", static_folder="static")

app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['ALLOWED_EXTENSTIONS'] = set(['mp4','avi'])

def allowed_file(filename):
	return '.' in filename and \
		filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSTIONS']

@app.route('/')
def main():
	curs = conn.cursor()
	curs.execute(load_sql)
	rows = curs.fetchall()
	return render_template('main.html', rows = rows)
	conn.close()

# def upload_success():
# 	return render_template('main.html')

@app.route('/detail/<title>/<int:anime_id>')
def anime_detail(title, anime_id):
	print anime_id
	curs = conn.cursor()
	curs.execute(load_detail_sql, (anime_id))
	rows = curs.fetchall()
	return render_template('detail.html', title = title, rows = rows)
	conn.close()

@app.route('/detail/<title>/<int:anime_id>/<int:episode>')
def show_anime(title, anime_id, episode):
	curs = conn.cursor()
	curs.execute(select_anipath_sql, (anime_id, episode))
	rows = curs.fetchall()
	anipath = rows[0][3]
	return render_template('watch.html', anipath=anipath)

@app.route('/upload')
def index():
	return render_template('upload.html')

@app.route('/uploaded', methods = ['POST'])
def upload():
	uploaded_files = request.files.getlist("file[]")
	filenames = []
	if request.method == 'POST':
		#get form data
		title = request.form.get('title')
		image = request.files['image']
		imgname = secure_filename(image.filename)

		image.save('static/images/'+imgname)
		print imgname
		#insert db from anime
		curs = conn.cursor()
		curs.execute(main_sql, (title, imgname))
		conn.commit()

		for index, file in enumerate(uploaded_files):
			if file and allowed_file(file.filename):
				filename = secure_filename(file.filename)
				if not os.path.exists(app.config['UPLOAD_FOLDER'] + title):
					os.makedirs(app.config['UPLOAD_FOLDER'] + title)
				insert_file_path = '/uploads/'+title+'/'+filename
				file.save(os.path.join(app.config['UPLOAD_FOLDER'] + title, filename))
				curs.execute(detail_sql,(title))
				row = curs.fetchall()
				curs.execute(insert_detail_sql, (row[0][0], index+1, insert_file_path, 1))
				conn.commit()
				filenames.append(filename)
			else:
				error_text = 'you can upload video extention'
				return render_template('upload.html', error_text=error_text)
		return render_template('uploaded.html', filenames=filenames)
		conn.close()
		


if __name__ == '__main__':
	app.run(debug=True)