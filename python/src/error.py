import os
import slackweb


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