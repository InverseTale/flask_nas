# -*- coding: utf-8 -*-
import os
from flask import Flask, url_for, g, render_template
from app.views.anime import bp as anime_bp
from app.views.upload import bp as upload_bp
from app.exts import db, migrate
from app.models.anime import Anime


def create_app():
    app = Flask(__name__)
    app.register_blueprint(anime_bp)
    app.register_blueprint(upload_bp)
    app.config.from_object('app.config')

    db.init_app(app)
    migrate.init_app(app, db)

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

    @app.route('/')
    def main():
        animes = Anime.query.all()
        return render_template('main.html', animes=animes)

    @app.route('/<int:anime_days>')
    def anime_days(anime_days):
        animes = Anime.query.filter(Anime.anime_days == anime_days).all()
        return render_template('main.html', animes=animes)

    return app
