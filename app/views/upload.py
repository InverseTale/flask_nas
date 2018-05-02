# -*- coding: utf-8 -*-
import os
from flask import Blueprint, render_template, request, current_app
from app.utils.change_vtt import change_vtt
from app.utils.smi2srt import convertSMI
from werkzeug.utils import secure_filename
from app.exts import db
from app.models.anime import Anime
from app.models.anime_detail import AnimeDetail
from sqlalchemy import desc

bp = Blueprint('upload', __name__)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in current_app.config[
               'ALLOWED_EXTENSTIONS']


def is_track_extenstion(filename):
    return '.smi' in filename


def create_new_anime(title, folder, img_name, anime_day):
    # insert db from anime

    anime = Anime(
        title=title,
        folder_name=folder,
        anime_image=img_name,
        anime_days=anime_day
    )
    db.session.add(anime)
    db.session.commit()


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

    insert_anime = Anime.query.filter(Anime.folder_name == folder).all()

    # create new anime
    if not insert_anime:
        create_new_anime(title, folder, img_name, anime_day)

    # checking all upload files
    for file in uploaded_files:
        select_anime = Anime.query.filter(Anime.folder_name == folder).first()

        anime_idx = select_anime.id

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

            episode = AnimeDetail.query.filter(
                AnimeDetail.anime_id == anime_idx).order_by(
                desc(AnimeDetail.episode)).first()
            print episode

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

                    insert_vtt = AnimeDetail.query.filter(
                        AnimeDetail.anime_id == anime_idx,
                        AnimeDetail.episode == get_episode).first()

                    insert_vtt.file_vtt = 'uploads/' + folder + '/' + new_filename
                    db.session.commit()

            else:
                get_episode = episode.episode + 1 if episode is not None else 1

                insert_detail = AnimeDetail(
                    anime_id=anime_idx,
                    episode=get_episode,
                    file=insert_file_path
                )
                db.session.add(insert_detail)
                db.session.commit()


            filenames.append(filename)
        else:
            error_text = 'you can upload video extention'
            return render_template('upload/upload.html', error_text=error_text)
    return render_template('upload/uploaded.html', filenames=filenames)
