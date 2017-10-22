# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug import secure_filename
from config import *
import subprocess, change_vtt, smi2srt
import os
app = Flask(__name__, static_url_path="", static_folder="static")

app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['ALLOWED_EXTENSTIONS'] = set(['mp4','avi','smi'])

def allowed_file(filename):
	return '.' in filename and \
		filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSTIONS']

def is_track_extenstion(filename):
	if '.smi' in filename:
		smi_ok = 'ok'
	else:
		smi_ok = 'no'
	return smi_ok

@app.route('/')
def main():
	curs = conn.cursor()
	curs.execute(load_sql)
	rows = curs.fetchall()
	return render_template('main.html', rows = rows)
	conn.close()

# def upload_success():
# 	return render_template('main.html')

@app.route('/detail/<folder_name>/<int:anime_id>')
def anime_detail(folder_name, anime_id):
	curs = conn.cursor()
	curs.execute(load_detail_sql, (anime_id))
	rows = curs.fetchall()
	return render_template('detail.html', folder_name = folder_name, rows = rows)
	conn.close()

@app.route('/detail/<folder_name>/<int:anime_id>/<int:episode>')
def show_anime(folder_name, anime_id, episode):
	curs = conn.cursor()
	curs.execute(select_anipath_sql, (anime_id, episode))
	anipath_rows = curs.fetchall()
	anipath = anipath_rows[0][3]

	subttile = anipath.split('.')
	subtitle_path = subttile[0]+'.vtt'
	print subtitle_path
	
	return render_template('watch.html', anipath = anipath, subtitle_path = subtitle_path)
	conn.close()

@app.route('/upload')
def index():
	return render_template('upload.html')

@app.route('/uploaded', methods = ['POST'])
def upload():
	uploaded_files = request.files.getlist("file[]")
	filenames = []
	episode = 0
	if request.method == 'POST':
		#get form data
		title = request.form.get('title')
		folder_name = request.form.get('folder_name')
		image = request.files['image']
		img_name = secure_filename(image.filename)

		image.save('static/images/'+img_name)
		print 'save imagename :' + img_name
		#insert db from anime
		curs = conn.cursor()
		curs.execute(search_anime_sql, folder_name)
		anime_row = curs.fetchall()
		if anime_row:
			pass
		else:
			curs.execute(main_sql, (title, folder_name, img_name))
			conn.commit()

		if not os.path.exists(app.config['UPLOAD_FOLDER'] + folder_name):
			os.makedirs(app.config['UPLOAD_FOLDER'] + folder_name)

		for file in uploaded_files:
			if file and allowed_file(file.filename):
				filename = secure_filename(file.filename)		

				insert_file_path = '/uploads/'+folder_name+'/'+filename
				print 'check extention .smi file : ' + is_track_extenstion(filename)
				file.save(os.path.join(app.config['UPLOAD_FOLDER'] + folder_name, filename))
				if is_track_extenstion(filename) == 'ok':
					run_subprocess = 'python smi2srt.py '+ folder_name + ' ' + filename
					print 'run_subprocess:' + run_subprocess
					subprocess.call([run_subprocess], shell=True)
					if '.smi' in filename:
						filename = filename.split('.')
						new_filename = filename[0] +'.vtt'
						insert_file_path = '/uploads/'+folder_name+'/'+new_filename
						change_vtt.change_vtt(insert_file_path)
						print("convert to smi file success!")
					else: 
						pass
				else:
					print '%'+folder_name+'%'
					curs.execute(check_detail_sql,('%'+folder_name+'%'))
					episode_row = curs.fetchall()
					print check_detail_sql + '%'+folder_name+'%'
					if episode_row:
						print 'have_episode'
						episode_row
						episode = episode_row[0][1] + 1
					else:
						episode+=1
						print 'did not have_episode'
					curs.execute(detail_sql, (folder_name))
					row = curs.fetchall()
					curs.execute(insert_detail_sql, (row[0][0], episode, insert_file_path, 1))
					conn.commit()
					filenames.append(filename)
			else:
				error_text = 'you can upload video extention'
				return render_template('upload.html', error_text=error_text)
		return render_template('uploaded.html', filenames=filenames)
		conn.close()
		


if __name__ == '__main__':
	app.run(debug=True, threaded=True)