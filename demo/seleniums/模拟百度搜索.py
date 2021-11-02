# -*-coding:utf-8-*-
__author__ = 'Administrator'

import time
from selenium import webdriver

# 1: 创建webdriver驱动：
driver = webdriver.Chrome()
# 2: 发送url请求
driver.get('https://www.baidu.com')
# 3: 操作页面：
driver.find_element_by_id("kw").send_keys("python")
driver.find_element_by_id("su").click()
time.sleep(2)
driver.save_screenshot("./python.png")
driver.close()
