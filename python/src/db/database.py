import mysql.connector as mysql
import os
import re


class DB:
    def __init__(self, logger, error):
        self.logger = logger
        self.error = error
        try:
            self.conn = mysql.connect(
                host=os.environ.get('DBHOST') or '127.0.0.1',
                port=os.environ.get('DBPORT') or '3306',
                user=os.environ.get('DBUSER'),
                password=os.environ.get('DBPASS'),
                database=os.environ.get('DBNAME') or ''
            )
        except KeyError as e:
            self.logger.error("Environment variable error")
            self.logger.error(e)
            self.error.send(str(e))
            exit(1)

        except mysql.errors.ProgrammingError as e:
            self.logger.error(e)
            self.error.send(str(e))
            exit(1)

        self.conn.ping(reconnect=True)
        logger.info("Connect to DB")

    def if_feed_exist(self, rows, url_in_feed):
        is_exists_in_db = False
        for row in rows:
            # title_on_db = row[0]  -> not use
            url_on_db = row[1]
            if url_on_db == url_in_feed:
                is_exists_in_db = True
                break
        return is_exists_in_db

    def if_title_update(self, rows, title_in_feed, url_in_feed):
        update_flg = False
        p = re.compile('([\d\.]+)更新')

        for row in rows:
            title_on_db = row[0]
            url_on_db = row[1]
            # urlは一緒だが title が異なる場合
            if (url_on_db == url_in_feed) and (title_on_db != title_in_feed):
                # パターンをぬき出せれば True
                if p.search(title_in_feed):
                    update_flg=True
                    return update_flg
                return update_flg
        return update_flg
