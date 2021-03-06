#! /usr/bin/python3

import urllib.request
import urllib.parse
import bs4
import re
import readline
import sys


class YouDao:
    @staticmethod
    def suggest(word):
        if not word.strip():
            return []
        url_prefix = 'https://dsuggest.ydstatic.com/suggest.s?query='
        data = urllib.request.urlopen(url_prefix + urllib.parse.quote(word)).read().decode('utf-8')
        soup = bs4.BeautifulSoup(urllib.parse.unquote(data), "html.parser")
        td = soup.find_all('td', class_='remindtt75')
        return [s.string for s in td]

    @staticmethod
    def result(word):
        response = []

        url_prefix = 'http://dict.youdao.com/w/'
        data = urllib.request.urlopen(url_prefix + urllib.parse.quote(word)).read().decode('utf-8')
        soup = bs4.BeautifulSoup(urllib.parse.unquote(data), "html.parser")

        pron = soup.find('div', class_='baav')
        if pron:
            pronounces = YouDao.list_join([YouDao.string_clean(e) for e in pron.strings])
            response.append(pronounces)

        collins_list = soup.find('div', class_='collinsToggle')
        if collins_list:
            for trans_list in collins_list.find_all('li'):
                trans = trans_list.find('div', class_='collinsMajorTrans')
                if trans:
                    response.append(
                        YouDao.highlight(word, YouDao.list_join([YouDao.string_clean(e) for e in trans.strings])))
                examples = trans_list.find('div', class_='exampleLists')
                if examples:
                    response.append(
                        YouDao.highlight(word, YouDao.list_join([YouDao.string_clean(e) for e in examples.strings])))
                response.append("")
        else:
            try:
                trans_list = soup.find('div', class_='trans-container').find_all('li')
                for li in trans_list:
                    response.append(li.string)
                trans_list = soup.find('div', class_='trans-container').find_all('p', class_='wordGroup')
                for li in trans_list:
                    response.append(YouDao.list_join([YouDao.string_clean(e) for e in li.strings]))
            except AttributeError:
                pass  # AttributeError: 'NoneType' object has no attribute 'find_all'

        return response

    @staticmethod
    def string_clean(word):
        return re.sub(r'\s+', ' ', word).strip(' \t\n\r')

    @staticmethod
    def list_join(li):
        return ' '.join(li).strip()

    @staticmethod
    def highlight(word, sentence):
        result = re.sub('^' + word + r'\s', '\033[92m' + word + '\033[0m ', sentence)
        result = re.sub(r'\s' + word + r'\s', ' \033[92m' + word + '\033[0m ', result)
        result = re.sub(r'\s' + word + '([,.?!"\':;])', r' \033[92m' + word + r"\033[0m\g<1>", result)
        return result


if __name__ == '__main__':
    suggest_buffer = {}


    def complete(word, state):
        if word not in suggest_buffer:
            suggest_buffer[word] = YouDao.suggest(word)

        return (suggest_buffer[word] + [None])[state]


    readline.parse_and_bind('tab: complete')
    readline.set_completer(complete)


    def translate_then_print(word):
        meanings = YouDao.result(word)
        for x in meanings:
            print(x)


    # when there are command line arguments, it will do the translation and exit
    # otherwise, it will enter the interactive mode
    if len(sys.argv) > 1:
        translate_then_print(' '.join(sys.argv[1:]))
        exit()

    # interactive mode
    print("YouDaoCLI")
    print("Press tab for suggestions")
    print("Press ctrl+d to exit")

    while True:
        try:
            line = input('> ')
            if not line.strip(' \t\n\r'):
                continue
            translate_then_print(line)
        except KeyboardInterrupt:
            print()
            pass
        except EOFError:
            print("\nExit.")
            exit()
