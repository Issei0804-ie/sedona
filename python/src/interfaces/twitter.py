import os
from requests_oauthlib import OAuth1Session  # OAuthのライブラリの読み込み

##########
LIVE_SERVER = 0
TEST_SERVER = 1
DRY_RUN = 2
##########


class Twitter:
    def __init__(self, status, logger, error):
        self.logger = logger
        self.error = error
        self.status = status
        try:
            self.api_key = os.environ.get('API_KEY')
            self.api_key_secret = os.environ.get('API_KEY_SECRET')
            self.access_token = os.environ.get('ACCESS_TOKEN')
            self.access_token_secret = os.environ.get('ACCESS_TOKEN_SECRET')
            self.endpoint = os.environ.get('TWITTER_ENDPOINT')
        except KeyError as e:
            self.logger.info(e)
            self.error.send(e)
            exit(1)
        self.twitter = OAuth1Session(self.api_key, self.api_key_secret, self.access_token, self.access_token_secret)  # 認証処理

    def send(self, title, link):
        tweet = title + "\n" + link
        params = {"status": tweet}
        self.logger.info("Tweets: " + title + "\n" + link)
        if self.status != DRY_RUN:
            res = self.twitter.post(url=self.endpoint, params=params)
            if res.status_code == 200:  # 正常投稿出来た場合
                self.logger.info("Success tweet")
            else:  # 正常投稿出来なかった場合
                self.logger.error(res.status_code)
                self.error.send(str(res.status_code) + res.reason)
                exit(1)

