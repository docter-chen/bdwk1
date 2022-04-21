# -*-coding:utf-8-*-
__author__ = 'Administrator'


from urllib.request import urlopen
from bs4 import BeautifulSoup
import re


'''
正则表达式结合bs使用
'''
html = urlopen("http://www.pythonscraping.com/pages/page3.html")
bsObj = BeautifulSoup(html)
images = bsObj.findAll("img",{"src":re.compile("\.\.\/img\/gifts/img.*\.jpg")})
for image in images:
 print(image["src"])