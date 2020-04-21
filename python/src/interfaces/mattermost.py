import slackweb
import logging
import os

##########
LIVE_SERVER = 0
TEST_SERVER = 1
DRY_RUN = 2
##########


class Mattermost:
    def __init__(self, status):
        self.webhook = ""  # mattermostのwebhook送信先
        self.status = status
        try:
            if status == LIVE_SERVER:
                self.webhook = os.environ.get('LIVE_HOOK_URL')
            elif status == TEST_SERVER:
                self.webhook = os.environ.get('TEST_HOOK_URL')
            elif status == DRY_RUN:
                self.webhook = ""
        except KeyError as e:
            logging.error(e)
            exit(1)


    def send(self, title, link):
        if self.status != DRY_RUN:
            mattermost = slackweb.Slack(url=self.webhook)
            mattermost.notify(text=title + "\n" + link)
        logging.info("webhook:" + self.webhook)
        logging.info("send to mattermost:" + title + "\n" + link)
