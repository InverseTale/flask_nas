from datetime import datetime
from app.exts import db


class AnimeDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    anime_id = db.Column(db.Integer, db.ForeignKey('anime.id'), nullable=False)
    episode = db.Column(db.Integer, nullable=False)
    file = db.Column(db.String(200), nullable=False)
    file_vtt = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

    anime = db.relationship('Anime',)

    __tablename__ = 'anime_detail'
    __table_args__ = {
        'extend_existing': True,
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8',
        'mysql_collate': 'utf8_general_ci'
    }
