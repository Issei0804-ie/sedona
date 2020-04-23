from logging import getLogger, StreamHandler, DEBUG, Formatter, FileHandler
import feedparser
import os
import db.database as db
import dotenv
import sys
import interfaces.twitter as twitter
import interfaces.mattermost as mattermost
import slackweb

#########################
# cronで回す時は相対パスを絶対パスにしないといけない
# スクリプトを実行した時のディレクトリからの相対パスであり、この main.py からの相対パスではない。
#########################

# endpointの設定
ENDPOINT = "http://rais.skr.u-ryukyu.ac.jp/dc/?feed=rss2"

ENVIRONMENT_FILE = "./../.env"

##########
LIVE_SERVER = 0
TEST_SERVER = 1
DRY_RUN = 2


##########


def main():
    status, logger, err = init()

    # ENDPOINTにアクセスしrssを取得
    logger.info("Access to endpoint")
    feeds = feedparser.parse(ENDPOINT)

    database = db.DB(logger=logger, error=err)
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
        # DB上に存在するか
        exist_flg = database.if_feed_exist(rows, url_in_feed)
        # タイトルの更新があったか
        update_flg = database.if_title_update(rows, title_in_feed, url_in_feed)
        # DBに存在しない or タイトルの更新があった
        if not exist_flg or update_flg:
            # dry-runの場合は実行しない
            if status != DRY_RUN:
                # 更新処理の場合
                if update_flg:
                    cur.execute("UPDATE feeds SET title=(%s) where url=(%s)", (title_in_feed, url_in_feed))
                # 新規作成処理の場合
                else:
                    cur.execute("INSERT INTO feeds VALUES (%s, %s)", (title_in_feed, url_in_feed))
                database.conn.commit()
            mm = mattermost.Mattermost(status, logger=logger, error=err)
            mm.send(title_in_feed, url_in_feed)
            tw = twitter.Twitter(status, logger=logger, error=err)
            tw.send(title=title_in_feed, link=url_in_feed)

    # セッションを切断
    cur.close()
    database.conn.close()
    logger.info("Successful completion")


def init_logger(modname=__name__):
    error_flg = False
    try:
        log_folder = os.environ.get('LOG_PATH')
    except KeyError:
        log_folder = "./../sedona.log"
        error_flg = True
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
    if error_flg:
        logger.info("Can not read LOG_PATH. \nPlease check environment variable.")
    return logger


# logging の設定と引数の処理を行います。 戻り値にスクリプト実行時の引数と logger を返します。.
def init():
    dotenv.load_dotenv(ENVIRONMENT_FILE)
    logger = init_logger(modname="debug")
    # loggingの設定
    logger.info("sedona start")
    # errorの設定
    error = Error(logger)
    # 引数の処理
    status = DRY_RUN  # とりあえず安全な値を初期値にする
    try:
        args = sys.argv
        if len(args) != 2:
            logger.error("Arguments Error")
            logger.error("Example python main.py dry-run")
            error.send("Arguments Error")
            exit(1)

        if args[1] == "live-server":
            logger.info("THIS IS LIVE-SERVER")
            status = LIVE_SERVER
        elif args[1] == "test-server":
            logger.info("THIS IS TEST-SERVER")
            status = TEST_SERVER
        elif args[1] == "dry-run":
            logger.info("THIS IS DRY-RUN")

    except KeyError as e:
        # .env関係のエラー
        logger.error("Environment variable error")
        logger.error(e)
        error.send(e)
        exit(1)
    return status, logger, error


class Error:
    def __init__(self, logger):
        try:
            self.address = os.environ.get('ADDRESS')
            self.logger = logger
            pass
        except KeyError as e:
            self.logger(e)
            exit(1)

    def send(self, message):
        error_chat_room = slackweb.Slack(url=self.address)
        error_chat_room.notify(text="From sedona: " + str(message))


if __name__ == '__main__':
    main()
