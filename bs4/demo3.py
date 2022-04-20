# -*-coding:utf-8-*-
__author__ = 'Administrator'

from urllib.request import urlopen
from bs4 import BeautifulSoup
html = urlopen("http://www.pythonscraping.com/pages/warandpeace.html")
bsObj = BeautifulSoup(html,features="lxml")

nameList = bsObj.findAll(text="the prince")
for name in nameList:
    print(name.get_text())

