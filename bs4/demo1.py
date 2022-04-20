# -*-coding:utf-8-*-
__author__ = 'Administrator'
from urllib.request import urlopen
from bs4 import BeautifulSoup
html = urlopen("http://www.pythonscraping.com/pages/page1.html")
bsObj = BeautifulSoup(html.read(),features="lxml")
print(bsObj.h1)