# -*- coding: utf-8 -*-

import requests
import time
from tqdm import tqdm
from bs4 import BeautifulSoup
import sys
# reload(sys)
# sys.setdefaultencoding('utf-8')


def get_content(target):
    req = requests.get(url = target)
    req.encoding = 'gbk'
    html = req.text
    bf = BeautifulSoup(html, 'lxml')
    texts = bf.find('div', id='content')
    content = texts.text.strip().split('\xa0'*4)
    return content

if __name__ == '__main__':
    server = 'https://www.zhhtxt.com'
    book_name = u'诡秘之主.txt'
    target = 'https://www.zhhtxt.com/2_2901/'
    req = requests.get(url=target)
    req.encoding = 'gbk'
    html = req.text
    bs = BeautifulSoup(html, 'lxml')
    chapters = bs.find('div', class_='listmain')##attrs={'class':'listmain'}
    print(chapters.text)
    chapters = chapters.find_all('a')
    for chapter in tqdm(chapters):
        chapter_name = chapter.string
        url = server + chapter.get('href')
        content = get_content(url)
        print(content)
        with open(book_name ,'a' ,encoding='gbk') as f:
            f.write('\n')
            f.write('\n'.join(content))
            f.write('\n')
        time.sleep(2)
