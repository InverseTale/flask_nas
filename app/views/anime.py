# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, g
from datetime import datetime, timedelta

bp = Blueprint('anime', __name__, url_prefix='/anime')


@bp.route('/detail/<int:anime_id>')
def anime_detail(anime_id):
    sql = g.db.get_sql('select_detail_sql')
    rows = g.db.execute(sql, anime_id)
    sql = g.db.get_sql('get_title')
    get_title = g.db.execute(sql, anime_id)
    title = get_title[0][0]
    return render_template('anime/detail.html', rows=rows, title=title)


@bp.route('/detail/<int:anime_id>/<int:episode>')
def show_anime(anime_id, episode):
    sql = g.db.get_sql('select_anipath_sql')
    rows = g.db.execute(sql, anime_id, episode)
    sql = g.db.get_sql('get_episode')
    episode_rows = g.db.execute(sql, anime_id)

    all_episode = episode_rows[0][0]
    next_episode = rows[0][2] + 1
    ani_path = rows[0][3]
    vtt_path = rows[0][4]
    return render_template('anime/watch.html', next_episode=next_episode,
                           all_episode=all_episode, ani_path=ani_path,
                           vtt_path=vtt_path)


@bp.route('/<int:anime_days>')
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

    return render_template('anime/../templates/main.html', rows=result)
