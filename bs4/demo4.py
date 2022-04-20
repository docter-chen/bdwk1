# -*-coding:utf-8-*-
__author__ = 'Administrator'

'''
标签 Tag 对象
'''
from urllib.request import urlopen
from bs4 import BeautifulSoup
html = urlopen("http://www.pythonscraping.com/pages/warandpeace.html")
bsObj = BeautifulSoup(html,features="lxml")

nameList = bsObj.div.h1
for name in nameList:
    print(name.get_text())

