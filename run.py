# -*- coding: utf-8 -*-
import os
from smi2srt import convertSMI
from datetime import datetime, timedelta

from flask import Flask, render_template, request, url_for, g
from werkzeug.utils import secure_filename

from change_vtt import change_vtt
from db import ANI_DB

app = Flask(__name__)
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
    return '.smi' in filename


def create_new_anime(row, title, folder, img_name, anime_day):
    # insert db from anime
    sql = g.db.get_sql('insert_anime_sql')
    g.db.execute(sql, title, folder, img_name, anime_day)
    g.db.commit()


@app.route('/')
def main():
    sql = g.db.get_sql('select_all_sql')
    rows = g.db.execute(sql)
    result = []
    for row in rows:
        now = datetime.now().replace(hour=0, minute=0, second=0)
        row = list(row)
        if row[5] >= now - timedelta(days=1):
            row.append(True)
        result.append(row)
    return render_template('main.html', rows=result)

@app.route('/<int:anime_days>')
def anime_days(anime_days):
    sql = g.db.get_sql('select_day_sql')
    rows = g.db.execute(sql, anime_days)
    result = []
    for row in rows:
        now = datetime.now().replace(hour=0, minute=0, second=0)
        row = list(row)
        if row[5] >= now - timedelta(days=1):
            row.append(True)
        result.append(row)

    return render_template('main.html', rows=result)


# def upload_success():
# 	return render_template('main.html')

@app.route('/detail/<int:anime_id>')
def anime_detail(anime_id):
    sql = g.db.get_sql('select_detail_sql')
    rows = g.db.execute(sql, anime_id)
    sql = g.db.get_sql('get_title')
    get_title = g.db.execute(sql, anime_id)
    title = get_title[0][0]
    return render_template('detail.html', rows=rows, title=title)


@app.route('/detail/<int:anime_id>/<int:episode>')
def show_anime(anime_id, episode):
    sql = g.db.get_sql('select_anipath_sql')
    rows = g.db.execute(sql, anime_id, episode)
    sql = g.db.get_sql('get_episode')
    episode_rows = g.db.execute(sql, anime_id)

    all_episode = episode_rows[0][0]
    next_episode = rows[0][2] + 1
    ani_path = rows[0][3]
    vtt_path = rows[0][4]
    return render_template('watch.html', next_episode=next_episode, all_episode=all_episode, ani_path=ani_path, vtt_path=vtt_path)


@app.route('/upload')
def index():
    return render_template('upload.html')


@app.route('/uploaded', methods=['POST'])
def upload():
    uploaded_files = request.files.getlist("file[]")
    filenames = []

    # get form data
    title = request.form.get('title')
    folder = request.form.get('folder_name')
    image = request.files['image']
    anime_day = request.form.get('anime_day')

    img_name = (image.filename)
    image.save('{}/static/images/{}'.format(
        app.config['BASE_DIR'],
        img_name
    ))

    sql = g.db.get_sql('select_anime_sql')
    row = g.db.execute(sql, title)

    # create new anime
    if not row:
        create_new_anime(row, title, folder, img_name, anime_day)

    # checking all upload files
    for index, file in enumerate(uploaded_files):
        sql = g.db.get_sql('select_anime_sql')
        row = g.db.execute(sql, title)
        g.db.commit()

        anime_idx = row[0][0]

        # check extenstions
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            # create new folder
            if not os.path.exists(app.config['UPLOAD_FOLDER'] + folder):
                os.makedirs(app.config['UPLOAD_FOLDER'] + folder)

            insert_file_path = 'uploads/' + folder + '/' + filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'] + folder,
                                   filename))

            sql = g.db.get_sql('get_episode')
            episode = g.db.execute(sql, anime_idx)

            if is_track_extenstion(filename):
                convertSMI(filename, folder)
                # .smi file > .vtt file
                if '.smi' in filename:
                    filename = filename.split('.')
                    new_filename = filename[0] + '.vtt'
                    insert_file_path = '{}{}/{}'.format(
                        app.config['UPLOAD_FOLDER'],
                        folder,
                        new_filename
                    )
                    change_vtt(insert_file_path)
                    sql = g.db.get_sql('select_anipath_sql')
                    vtt = g.db.execute(sql, anime_idx, get_episode)
                    vtt_idx = vtt[0][1]

                    sql = g.db.get_sql('insert_file_vtt')
                    g.db.execute(sql,
                                 'uploads/' + folder + '/' + new_filename,
                                 vtt_idx, get_episode)
                    g.db.commit()

            else:
                get_episode = episode[0][0] + 1 if episode[0][0] else 1

                sql = g.db.get_sql('insert_detail_sql')
                g.db.execute(sql, anime_idx, get_episode, insert_file_path)
                g.db.commit()

            filenames.append(filename)
        else:
            error_text = 'you can upload video extention'
            return render_template('upload.html', error_text=error_text)
    return render_template('uploaded.html', filenames=filenames)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
