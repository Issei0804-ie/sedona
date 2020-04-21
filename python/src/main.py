from logging import getLogger, StreamHandler, DEBUG, Formatter, FileHandler
import feedparser
import datetime
import db.database as db
import dotenv
import sys
import interfaces.mattermost as mattermost
import slackweb

#########################
# cronで回す時は相対パスを絶対パスにしないといけない
# スクリプトを実行した時のディレクトリからの相対パスであり、この main.py からの相対パスではない。
#########################

# endpointの設定
ENDPOINT = "http://rais.skr.u-ryukyu.ac.jp/dc/?feed=rss2"

# エラーが起きた際にこの webhook にエラー内容を送信する。
MYADDRESS = ""

ENVIRONMENTFILE = "./../.env"

##########
LIVE_SERVER = 0
TEST_SERVER = 1
DRY_RUN = 2


##########


def main():
    status, logger = init()

    # ENDPOINTにアクセスしrssを取得
    logger.info("Access to endpoint")
    feeds = feedparser.parse(ENDPOINT)

    database = db.DB(logger=logger)
    cur = database.conn.cursor()

    cur.execute("select * from feeds")
    # DB上のデータを取得
    rows = cur.fetchall()
    database.conn.commit()

    feed_count = len(feeds['entries'])  # 処理するfeedの量
    for i in range(feed_count):
        # タイトル, リンクを取得
        title_in_feed = feeds['entries'][i]['title']
        url_in_feed = feeds['entries'][i]['link']
        # DB上に存在しなければ
        if not database.if_feed_exist(rows, url_in_feed):
            if status != DRY_RUN:  # dry-runの場合は実行しない
                cur.execute("INSERT INTO feeds VALUES (%s, %s)", (title_in_feed, url_in_feed))
                database.conn.commit()
            mm = mattermost.Mattermost(status, logger=logger)
            mm.send(title_in_feed, url_in_feed)

    # セッションを切断
    cur.close()
    database.conn.close()
    logger.info("Successful completion")


def init_loger(log_folder, modname=__name__):
    logger = getLogger(modname)
    logger.setLevel(DEBUG)

    sh = StreamHandler()
    sh.setLevel(DEBUG)
    formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    sh.setFormatter(formatter)
    logger.addHandler(sh)

    fh = FileHandler(log_folder)  # fh = file handler
    fh.setLevel(DEBUG)
    fh_formatter = Formatter('%(asctime)s - %(filename)s - %(name)s - %(lineno)d - %(levelname)s - %(message)s')
    fh.setFormatter(fh_formatter)
    logger.addHandler(fh)
    return logger


# logging の設定と引数の処理を行います。 戻り値にスクリプト実行時の引数と logger を返します。.
def init():
    logger = init_loger(log_folder="./../sedona.log", modname="debug")
    # loggingの設定
    logger.info("sedona start")

    # 引数の処理
    status = DRY_RUN  # とりあえず安全な値を初期値にする
    try:
        dotenv.load_dotenv(ENVIRONMENTFILE)
        args = sys.argv
        if args[1] == "live-server":
            logger.info("THIS IS LIVE-SERVER")
            status = LIVE_SERVER
        elif args[1] == "test-server":
            logger.info("THIS IS TEST-SERVER")
            status = TEST_SERVER
        elif args[1] == "dry-run":
            logger.info("THIS IS DRY-RUN")
        else:
            logger.error("Arguments Error")
            logger.error("example python main.py dry-run")
            error("Arguments Error")
            exit(1)

    except KeyError as e:
        # .env関係のエラー
        logger.error("Environment variable error")
        logger.error(e)
        error(e)
        exit(1)
    except IndexError as e:
        # 引数関係のエラー
        logger.error(e)
        error(e)
        exit(1)

    return status, logger


def error(message):
    error_chat_room = slackweb.Slack(url=MYADDRESS)
    error_chat_room.notify(text="From sedona: " + str(message))


if __name__ == '__main__':
    main()
