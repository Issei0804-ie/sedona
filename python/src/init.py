import dotenv
import sys
import os
from logging import getLogger, StreamHandler, DEBUG, Formatter, FileHandler
import error as myerror

##########
LIVE_SERVER = 0
TEST_SERVER = 1
DRY_RUN = 2
SYNC = 3
##########
ENVIRONMENT_FILE = "./../.env"


# logging の設定と引数の処理を行います。 戻り値にスクリプト実行時の引数と logger を返します。.
def init():
    dotenv.load_dotenv(ENVIRONMENT_FILE)
    logger = init_logger(modname="debug")
    # loggingの設定
    logger.info("sedona start")
    # errorの設定
    error = myerror.Error(logger)
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
            status = DRY_RUN
        elif args[1] == "sync":
            logger.info("THIS IS SYNC")
            status = SYNC

    except KeyError as e:
        # .env関係のエラー
        logger.error("Environment variable error")
        logger.error(e)
        error.send(e)
        exit(1)
    return status, logger, error


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

    # log_folfer がない時の error 処理
    fh = FileHandler(log_folder)  # fh = file handler
    fh.setLevel(DEBUG)
    fh_formatter = Formatter('%(asctime)s - %(filename)s - %(name)s - %(lineno)d - %(levelname)s - %(message)s')
    fh.setFormatter(fh_formatter)
    logger.addHandler(fh)
    if error_flg:
        logger.info("Can not read LOG_PATH. \nPlease check environment variable.")
    return logger
