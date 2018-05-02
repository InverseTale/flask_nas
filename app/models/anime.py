from datetime import datetime, timedelta
from sqlalchemy import desc
from sqlalchemy.ext.declarative import declared_attr
from app.exts import db


class Anime(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.String(200), unique=True, nullable=False)
    folder_name = db.Column(db.String(200), unique=True, nullable=False)
    anime_image = db.Column(db.String(200), nullable=True)
    anime_days = db.Column(db.Integer, nullable=False)
    register_date = db.Column(
        db.DateTime, default=datetime.now, nullable=False
    )

    __tablename__ = 'anime'
    __table_args__ = {
        'extend_existing': True,
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8',
        'mysql_collate': 'utf8_general_ci'
    }

    @property
    def is_new(self):
        from app.models.anime_detail import AnimeDetail
        now = datetime.now().replace(hour=0, minute=0, second=0)
        anime_detail = AnimeDetail.query \
            .filter(AnimeDetail.anime_id == self.id) \
            .order_by(desc(AnimeDetail.id)) \
            .first()
        if anime_detail:
            return anime_detail.created_at >= now - timedelta(days=1)
        else:
            return False

    @declared_attr
    def anime_details(self):
        from app.models.anime_detail import AnimeDetail
        return db.relationship(AnimeDetail, order_by="asc(AnimeDetail.episode)")
