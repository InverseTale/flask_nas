import pymysql

conn = pymysql.connect(host='localhost', user='root', 
            password='1111', db='nas', charset='utf8')

main_sql = """insert into anime(title, anime_image) values(%s, %s)"""
load_sql = """select * from anime"""
load_detail_sql = """select * from anime_detail where anime_id = %s"""
select_anipath_sql = """select * from anime_detail where anime_id = %s and episode = %s"""
detail_sql = """select * from anime where title = %s"""
insert_detail_sql = """insert into anime_detail(anime_id, episode, file, end_yn) values(%s, %s, %s ,%s)"""
