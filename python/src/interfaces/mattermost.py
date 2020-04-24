import slackweb
import os

##########
LIVE_SERVER = 0
TEST_SERVER = 1
DRY_RUN = 2
SYNC = 3
##########


class Mattermost:
    def __init__(self, status, logger, error):
        self.webhook = ""  # 送信先
        self.status = status
        self.logger = logger
        self.error = error
        try:
            if status == LIVE_SERVER:
                self.webhook = os.environ.get('LIVE_HOOK_URL')
            elif status == TEST_SERVER:
                self.webhook = os.environ.get('TEST_HOOK_URL')
            elif status == DRY_RUN:
                self.webhook = ""
        except KeyError as e:
            self.logger.error(e)
            self.error.send(str(e))
            exit(1)


    def send(self, title, link):
        if self.status != DRY_RUN:
            mattermost = slackweb.Slack(url=self.webhook)
            mattermost.notify(text=title + "\n" + link)
        self.logger.info("webhook:" + self.webhook)
        self.logger.info("send to mattermost:" + title + "\n" + link)
