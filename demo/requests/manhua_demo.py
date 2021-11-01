# -*-coding:utf-8-*-
__author__ = 'Administrator'

import requests
from bs4 import BeautifulSoup

target_url = "https://www.dmzj.com/info/yaoshenji.html"
#获取url的request
r = requests.get(url=target_url)

#构建一个BS
bs = BeautifulSoup(r.text, 'lxml')

#找标签及class
list_con_li = bs.find('ul', class_="list_con_li")

#找所有标签
comic_list = list_con_li.find_all('a')
chapter_names = []
chapter_urls = []

#遍历所有标签
for comic in comic_list:
    print(comic.text)
    href = comic.get('href')
    name = comic.text
    chapter_names.insert(0, name)
    chapter_urls.insert(0, href)

print(chapter_names)
print(chapter_urls)

https://images.dmzj.com/img/chapterpic/3059/96396/15272970354818.jpg
https://images.dmzj.com/img/chapterpic/3059/14237/14395217739069.jpg