# -*-coding:utf-8-*-
__author__ = 'Administrator'

import requests

url = 'https://wenku.baidu.com/view/3ff9c862ed3a87c24028915f804d2b160a4e868d.html'
header = {'User-agent': 'Googlebot'}
res = requests.get(url, headers=header)
res.url
