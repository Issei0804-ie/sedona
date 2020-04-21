import logging
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

ENVIRONMENTFILE = "./../sample.env"

##########
LIVE_SERVER = 0
TEST_SERVER = 1
DRY_RUN = 2
##########


def main():
    status = init()

    # 現在時刻をログに記載
    logging.info(datetime.datetime.now())

    # ENDPOINTにアクセスしrssを取得
    feeds = feedparser.parse(ENDPOINT)

    conn = db.mysql_connecter()
    cur = conn.cursor()

    cur.execute("select * from feeds")
    # DB上のデータを取得
    rows = cur.fetchall()
    conn.commit()

    feed_count = len(feeds['entries'])  # 処理するfeedの量
    for i in range(feed_count):
        # タイトル, リンクを取得
        title_in_feed = feeds['entries'][i]['title']
        url_in_feed = feeds['entries'][i]['link']
        # DB上に存在しなければ
        if not db.if_feed_exist(rows, url_in_feed):
            if status != DRY_RUN:  # dry-runの場合は実行しない
                cur.execute("INSERT INTO feeds VALUES (%s, %s)", (title_in_feed, url_in_feed))
                conn.commit()
            mm = mattermost.Mattermost(status)
            mm.send(title_in_feed, url_in_feed)

    # セッションを切断
    cur.close()
    conn.close()


# logging の設定と引数の処理を行います。 戻り値にスクリプトの引数を返します。
def init():
    # loggingの設定
    logging.basicConfig(filename='./../sedona.log', level=logging.DEBUG)
    logging.info("**** sedona start ****")

    # 引数の処理
    status = DRY_RUN  # とりあえず安全な値を初期値にする
    try:
        dotenv.load_dotenv(ENVIRONMENTFILE)
        args = sys.argv
        if args[1] == "live-server":
            logging.info("****** THIS IS LIVE-SERVER ******")
            status = LIVE_SERVER
        elif args[1] == "test-server":
            logging.info("****** THIS IS TEST-SERVER ******")
            status = TEST_SERVER
        elif args[1] == "dry-run":
            logging.info("****** THIS IS DRY-RUN ******")
        else:
            logging.error("Arguments Error")
            logging.error("*****  (example) python main.py dry-run  *****")
            error("Arguments Error")
            exit(1)

    except KeyError as e:
        # .env関係のエラー
        logging.error("Environment variable error")
        logging.error(e)
        error(e)
        exit(1)
    except IndexError as e:
        # 引数関係のエラー
        logging.error(e)
        error(e)
        exit(1)

    return status


def error(message):
    error_chat_room = slackweb.Slack(url=MYADDRESS)
    error_chat_room.notify(text="From sedona: " + str(message))


if __name__ == '__main__':
    main()
