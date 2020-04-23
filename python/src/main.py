import feedparser
import db.database as db
import interfaces.twitter as twitter
import interfaces.mattermost as mattermost
import init

#########################
# cronで回す時は相対パスを絶対パスにしないといけない
# スクリプトを実行した時のディレクトリからの相対パスであり、この main.py からの相対パスではない。
#########################

# endpointの設定
ENDPOINT = "http://rais.skr.u-ryukyu.ac.jp/dc/?feed=rss2"



##########
LIVE_SERVER = 0
TEST_SERVER = 1
DRY_RUN = 2
##########


def main():
    status, logger, err = init.init()

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


if __name__ == '__main__':
    main()
