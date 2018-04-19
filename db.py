import pymysql
from flask import current_app

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

class ANI_DB(object):
    def __init__(self):
        self.conn = pymysql.connect(
            host=current_app.config['DB_HOST'],
            user=current_app.config['DB_USER'],
            password=current_app.config['DB_PASSWORD'],
            db=current_app.config['DB_DB'],
            charset=current_app.config['DB_CHARSET']
        )

    def close(self):
        self.conn.close()

    def execute(self, sql, *args):
        curs = self.conn.cursor()
        curs.execute(sql, args)
        rows = curs.fetchall()
        return rows

    def commit(self):
        self.conn.commit()

    def get_sql(self, sql):
        return {
            'insert_anime_sql': "insert into anime(title, folder_name, anime_image, anime_days) values(%s, %s, %s, %s)",
            'insert_detail_sql': "insert into anime_detail(anime_id, episode, file) values(%s, %s, %s)",
            'insert_file_vtt': "update  anime_detail set file_vtt = %s where anime_id = %s and episode = %s",
            'select_all_sql': "select * from anime",
            'select_detail_sql': "select * from anime_detail where anime_id = %s",
            'select_anipath_sql': "select * from anime_detail where anime_id = %s and episode = %s",
            'select_anime_sql': "select * from anime where title = %s",
            'select_day_sql': "select * from anime where anime_days = %s ",
            'get_episode': "select max(episode) from anime_detail where anime_id = %s",
            'get_title': "select title from anime where id = %s"
        }.get(sql, None)
