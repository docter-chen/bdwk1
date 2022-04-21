# -*-coding:utf-8-*-
__author__ = 'Administrator'


'''
想找出子标签，可以用 .children 标签
'''
from urllib.request import urlopen
from bs4 import BeautifulSoup
html = urlopen("https://wenku.baidu.com/search?word=excel&lm=&od=0&fr=&ie=utf-8")
bsObj = BeautifulSoup(html,features="lxml")
print(bsObj)
url_lists = bsObj.find_all("a",{"class":"search-result-title_2af18"})

for urllist in url_lists:
    # urllist.a
    print(urllist)
