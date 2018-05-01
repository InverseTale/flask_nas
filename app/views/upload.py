# -*- coding: utf-8 -*-
import os
from flask import Blueprint, render_template, request, g, current_app
from app.utils.change_vtt import change_vtt
from app.utils.smi2srt import convertSMI
from werkzeug.utils import secure_filename

bp = Blueprint('upload', __name__, url_prefix='/upload')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in current_app.config[
               'ALLOWED_EXTENSTIONS']


def is_track_extenstion(filename):
    return '.smi' in filename


def create_new_anime(row, title, folder, img_name, anime_day):
    # insert db from anime
    sql = g.db.get_sql('insert_anime_sql')
    g.db.execute(sql, title, folder, img_name, anime_day)
    g.db.commit()


@bp.route('/upload')
def index():
    return render_template('upload/upload.html')


@bp.route('/uploaded', methods=['POST'])
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
        current_app.config['BASE_DIR'],
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
            if not os.path.exists(
                    current_app.config['UPLOAD_FOLDER'] + folder):
                os.makedirs(current_app.config['UPLOAD_FOLDER'] + folder)

            insert_file_path = 'uploads/' + folder + '/' + filename
            file.save(
                os.path.join(current_app.config['UPLOAD_FOLDER'] + folder,
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
                        current_app.config['UPLOAD_FOLDER'],
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
            return render_template('upload/upload.html', error_text=error_text)
    return render_template('upload/uploaded.html', filenames=filenames)
