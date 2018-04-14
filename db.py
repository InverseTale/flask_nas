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
            'main_sql': "insert into anime(title, folder_name, anime_image) values(%s, %s, %s)",
            'load_sql': "select * from anime",
            'load_detail_sql': "select * from anime_detail where anime_id = %s",
            'select_anipath_sql': "select * from anime_detail where anime_id = %s and episode = %s",
            'detail_sql': "select * from anime where title = %s",
            'insert_detail_sql': "insert into anime_detail(anime_id, episode, file, end_yn) values(%s, %s, %s ,%s)",
            'insert_file_vtt': "update  anime_detail set file_vtt = %s where anime_id = %s and episode = %s",
            'get_episode' : "select max(episode) from anime_detail where anime_id = %s"
        }.get(sql, None)
