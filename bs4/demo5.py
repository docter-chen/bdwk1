# -*-coding:utf-8-*-
__author__ = 'Administrator'


'''
想找出子标签，可以用 .children 标签
'''
from urllib.request import urlopen
from bs4 import BeautifulSoup
html = urlopen("https://wenku.baidu.com/search?word=%E7%AD%94%E6%A1%88&lm=0&od=0&fr=top_home&ie=utf-8")
bsObj = BeautifulSoup(html,features="lxml")
for child in bsObj.find("table",{"id":"giftList"}).children:
    print(child)
