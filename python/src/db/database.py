import logging
import mysql.connector as mysql
import os


def mysql_connecter():
    try:
        conn = mysql.connect(
            host=os.environ.get('DBHOST') or '127.0.0.1',
            port=os.environ.get('DBPORT')or '3306',
            user=os.environ.get('DBUSER'),
            password=os.environ.get('DBPASS'),
            database=os.environ.get('DBNAME') or ''
        )


    except KeyError as e:
        logging.error("Environment variable error")
        logging.error(e)
        exit(1)

    conn.ping(reconnect=True)
    logging.info("we can connect to DB")
    return conn


def if_feed_exist(rows, url_in_feed):
    is_exists_in_db = False
    for row in rows:
        # title_on_db = row[0]  -> not use
        url_on_db = row[1]
        if url_on_db == url_in_feed:
            is_exists_in_db = True
            break
    return is_exists_in_db