# -*-coding:utf-8-*-
__author__ = 'Administrator'
'''
lambda表达式
BeautifulSoup 允许我们把特定函数类型当作 findAll 函数的参数。唯一的限制条件是这些
函数必须把一个标签作为参数且返回结果是布尔类型。BeautifulSoup 用这个函数来评估它
遇到的每个标签对象，最后把评估结果为“真”的标签保留，把其他标签剔除。
'''


from urllib.request import urlopen
from bs4 import BeautifulSoup
import re


html = urlopen("http://www.pythonscraping.com/pages/page3.html")
bsObj = BeautifulSoup(html,features="lxml")
images = bsObj.findAll(lambda tag: len(tag.attrs) == 2)
for image in images:
 print(image)
 # print(image["src"])