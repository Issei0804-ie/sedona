from unittest import TestCase
import db.database as mysql
from unittest.mock import MagicMock


class TestDB(TestCase):
    rows = [
        ["遠隔授業に関するまとめページを作成しました", "http://EXAMPLE.JP/?p=10285"],
        ["令和２年度前学期の共通教育等科目の履修登録調整について（通知）", "http://EXAMPLE.JP/?p=10210"],
        ["学生の皆さんへ（遠隔授業を受けるにあたって）（2020.04.01更新）", "http://EXAMPLE.JP/?p=10317"]
    ]

    def test_if_title_update(self):
        testcases = [
            [self.rows, "遠隔授業に関するまとめページを作成しました", "http://EXAMPLE.JP/?p=10285", False],
            [self.rows, "遠隔授業に関するまとめページを作成しました", "http://EXAMPLE.JP/?p=20000", False],
            [self.rows, "遠隔授業に関するまとめページを作成しました（タイトル追加）", "http://EXAMPLE.JP/?p=10285", False],
            [self.rows, "遠隔授業に関するまとめページを作成しました(2020.04.01更新)", "http://EXAMPLE.JP/?p=10285", True],
            [self.rows, "", "http://EXAMPLE.JP/?p=10023", False],
            [self.rows, "　", "http://EXAMPLE.JP/?p=9462", False],
            [self.rows, " ", "http://EXAMPLE.JP/?p=85036", False]
        ]

        db = mock_db()
        for testcase in testcases:
            result = db.if_title_update(testcase[0], testcase[1], testcase[2])
            self.assertEqual(result, testcase[3], testcase)

    def test_if_feed_exist(self):

        testcases = [
            [self.rows, "http://EXAMPLE.JP/?p=10000", False],
            [self.rows, "http://EXAMPLE.JP/?p=10317", True],
            [self.rows, "", False],
            [self.rows, "　", False],
            [self.rows, " ", False]
        ]
        db = mock_db()
        for testcase in testcases:
            result = db.if_feed_exist(testcase[0], testcase[1])
            self.assertEqual(result, testcase[2], testcase)


class mock_db(mysql.DB):
    def __init__(self):
        pass