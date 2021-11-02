# -*-coding:utf-8-*-
__author__ = 'Administrator'

from selenium import webdriver

driver = webdriver.Chrome()
driver.get("https:www.baidu.com")
# 1: 得到的数据是列表套字典的形式：
cookies = driver.get_cookies()
print(driver.get_cookies())

# 2: 将cookies转换成字典
cookies_dict = {cookie['name']: cookie['value'] for cookie in cookies}
print(cookies_dict)

# 3: 删除指定的cookie
driver.delete_cookie('BAIDUID_BFESS')

# 4： 删除所有的cookies
driver.delete_all_cookies()
