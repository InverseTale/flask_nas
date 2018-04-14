# -*- coding: utf-8 -*-
import os
import subprocess
import change_vtt
import smi2srt
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, \
    send_from_directory, g
from db import ANI_DB

app = Flask(__name__, static_url_path="", static_folder="static")
app.config.from_object('config')


@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)


def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)


@app.before_request
def before_request():
    g.db = ANI_DB()


@app.after_request
def after_request(response):
    g.db.close()
    return response


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
    sql = g.db.get_sql('load_sql')
    rows = g.db.execute(sql)
    result = []
    for row in rows:
        now = datetime.now().replace(hour=0, minute=0, second=0)
        row = list(row)
        if row[4] >= now - timedelta(days=1):
            row.append(True)
        result.append(row)
    return render_template('main.html', rows=result)


# def upload_success():
# 	return render_template('main.html')

@app.route('/detail/<title>/<int:anime_id>')
def anime_detail(title,anime_id):
    sql = g.db.get_sql('load_detail_sql')
    rows = g.db.execute(sql, anime_id)
    return render_template('detail.html', rows=rows, title=title)


@app.route('/detail/<int:anime_id>/<int:episode>')
def show_anime(anime_id, episode):
    sql = g.db.get_sql('select_anipath_sql')
    rows = g.db.execute(sql, anime_id, episode)
    anipath = rows[0][3]
    vttpath = rows[0][4]
    return render_template('watch.html', anipath=anipath, vttpath=vttpath)


@app.route('/upload')
def index():
    return render_template('upload.html')


@app.route('/uploaded', methods=['POST'])
def upload():
    uploaded_files = request.files.getlist("file[]")
    filenames = []
    if request.method == 'POST':
        # get form dfolder_nameata
        title = request.form.get('title')
        folder = request.form.get('folder_name')
        image = request.files['image']
        imgname = secure_filename(image.filename)

        image.save('/home/ubuntu/flask_nas/static/images/' + imgname)

        sql = g.db.get_sql('detail_sql')
        row = g.db.execute(sql, title)

        if not row:
            # insert db from anime
            sql = g.db.get_sql('main_sql')
            g.db.execute(sql, title, folder, imgname)
            g.db.commit()
            print 'insert anime ok!'

        for index, file in enumerate(uploaded_files):
            sql = g.db.get_sql('detail_sql')
            row = g.db.execute(sql, title)
            g.db.commit()
            print 'row is :'
            print row
            print row[0][0]

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)

                if not os.path.exists(app.config['UPLOAD_FOLDER'] + folder):
                    os.makedirs(app.config['UPLOAD_FOLDER'] + folder)
                insert_file_path = '/uploads/' + folder + '/' + filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'] + folder,
                                       filename))

                sql = g.db.get_sql('get_episode')
                episode = g.db.execute(sql, row[0][0])

                print episode[0][0]

                if is_track_extenstion(filename) == 'no':
                    if episode[0][0] is None:
                        get_episode = 1
                        print 'new row'
                        print get_episode
                    else:
                        print 'not new row'
                        get_episode = episode[0][0] + 1
                        print get_episode
                    sql = g.db.get_sql('insert_detail_sql')
                    g.db.execute(sql, row[0][0], get_episode, insert_file_path, 1)
                    g.db.commit()
                    print 'insert detail sql success!'
                elif is_track_extenstion(filename) == 'ok':
                    run_subprocess = 'python smi2srt.py ' + folder + ' ' + filename
                    subprocess.call(
                        ['python smi2srt.py ' + folder + ' ' + filename],
                        shell=True)
                    if '.smi' in filename:
                        filename = filename.split('.')
                        new_filename = filename[0] + '.vtt'
                        insert_file_path = app.config['UPLOAD_FOLDER'] + folder + '/' + new_filename
                        change_vtt.change_vtt(insert_file_path)

                        print  row[0][0]
                        print get_episode
                        sql = g.db.get_sql('select_anipath_sql')
                        vtt = g.db.execute(sql, row[0][0], get_episode)
                        print 'is vtt: '
                        print vtt
                        sql= g.db.get_sql('insert_file_vtt')
                        g.db.execute(sql, '/uploads/' + folder + '/' + new_filename, vtt[0][1], get_episode)
                        g.db.commit()

                    else:
                        pass

                filenames.append(filename)
            else:
                error_text = 'you can upload video extention'
                return render_template('upload.html', error_text=error_text)
        return render_template('uploaded.html', filenames=filenames)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
