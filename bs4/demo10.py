# -*-coding:utf-8-*-
__author__ = 'Administrator'

from urllib.request import urlopen
from bs4 import BeautifulSoup
html = urlopen("https://wenku.baidu.com/search?word=excel&lm=&od=0&fr=&ie=utf-8")
bsObj = BeautifulSoup(html,features="lxml")
for link in bsObj.findAll("a"):
    if 'href' in link.attrs:
        print(link.attrs['href'])