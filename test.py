#! /usr/bin/python3

from youdaocli import YouDao


if __name__ == '__main__':
    print(YouDao.suggest('dict'))
    print(YouDao.result('dictionary'))
