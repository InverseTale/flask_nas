import os
from flask import Flask, url_for, g, render_template
from app.views.anime import bp as anime_bp
from app.views.upload import bp as upload_bp
from app.utils.db import ANI_DB
from datetime import datetime, timedelta


def create_app():
    app = Flask(__name__)
    app.register_blueprint(anime_bp)
    app.register_blueprint(upload_bp)
    app.config.from_object('app.config')

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

    return app
