# -*- coding: utf-8 -*-
from flask import Blueprint, render_template
from app.models.anime_detail import AnimeDetail
from app.models.anime import Anime
from sqlalchemy import asc

bp = Blueprint('anime', __name__, url_prefix='/anime')


@bp.route('/detail/<int:anime_id>')
def anime_detail(anime_id):
    anime = Anime.query.filter(Anime.id == anime_id).first()
    rows = anime.anime_details
    title = anime.title
    return render_template('anime/detail.html', rows=rows, title=title)


@bp.route('/detail/<int:anime_id>/<int:episode>')
def show_anime(anime_id, episode):
    details = AnimeDetail.query \
        .filter(
        AnimeDetail.anime_id == anime_id,
        AnimeDetail.episode >= episode
    ) \
        .order_by(asc(AnimeDetail.episode)) \
        .limit(2) \
        .all()

    has_next_episode = len(details) > 1
    current_detail = details[0]

    return render_template('anime/watch.html',
                           has_next_episode=has_next_episode,
                           current_detail=current_detail)
