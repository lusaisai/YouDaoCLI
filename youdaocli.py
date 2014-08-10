#! /usr/bin/python3

import urllib.request
import urllib.parse
import bs4
import re
import readline


class YouDao:
    @staticmethod
    def suggest(word):
        if not word.strip():
            return []
        url_prefix = 'http://dsuggest.ydstatic.com/suggest/suggest.s?query='
        data = urllib.request.urlopen(url_prefix + urllib.parse.quote(word)).read().decode('utf-8')
        soup = bs4.BeautifulSoup(urllib.parse.unquote(data))
        td = soup.find_all('td', class_='remindtt75')
        return [s.string for s in td]

    @staticmethod
    def result(word):
        response = []

        url_prefix = 'http://dict.youdao.com/search?q='
        data = urllib.request.urlopen(url_prefix + urllib.parse.quote(word)).read().decode('utf-8')
        soup = bs4.BeautifulSoup(urllib.parse.unquote(data))

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
            trans_list = soup.find('div', class_='trans-container').find_all('li')
            for li in trans_list:
                response.append(li.string)
            trans_list = soup.find('div', class_='trans-container').find_all('p', class_='wordGroup')
            for li in trans_list:
                response.append(YouDao.list_join([YouDao.string_clean(e) for e in li.strings]))

        return response

    @staticmethod
    def string_clean(word):
        return re.sub('\s+', ' ', word).strip(' \t\n\r')

    @staticmethod
    def list_join(li):
        return ' '.join(li).strip()

    @staticmethod
    def highlight(word, sentence):
        result = re.sub('^' + word + '\s', '\033[92m' + word + '\033[0m ', sentence)
        result = re.sub('\s' + word + '\s', ' \033[92m' + word + '\033[0m ', result)
        result = re.sub('\s' + word + '([,.?!"\':;])', ' \033[92m' + word + "\033[0m\g<1>", result)
        return result


# CLI support
suggest_buffer = {}


def complete(word, state):
    if not word in suggest_buffer:
        suggest_buffer[word] = YouDao.suggest(word)

    return (suggest_buffer[word] + [None])[state]


readline.parse_and_bind('tab: complete')
readline.set_completer(complete)

print("YouDaoCLI")
print("Press tab for suggestions")
print("Press ctrl+d to exit")

while True:
    try:
        line = input('> ')
        if not line.strip(' \t\n\r'):
            continue
        meanings = YouDao.result(line)
        for x in meanings:
            print(x)
    except KeyboardInterrupt:
        print()
        pass
    except EOFError:
        print("\nExit.")
        exit()
