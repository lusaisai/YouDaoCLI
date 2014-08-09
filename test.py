#! /usr/bin/python3

import unittest
from youdaocli import YouDao

class MyTestCase(unittest.TestCase):
    def test_suggest(self):
        print(YouDao.suggest('dict'))
        print(YouDao.suggest('dicttcid'))

    def test_result(self):
        print(YouDao.result('dictionary'))
        print(YouDao.result('tree'))


if __name__ == '__main__':
    unittest.main()
