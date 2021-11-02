# -*-coding:utf-8-*-
__author__ = 'Administrator'

import time

from selenium import webdriver

# 1: 创建驱动对象
driver = webdriver.Chrome()
# 2：打开一个网页
driver.get("http://www.baidu.com")
driver.find_element_by_id('kw').send_keys('python')
driver.find_element_by_id('su').click()
time.sleep(1)

# 3: 使用js语句打开新的页面：
js = 'window.open("https://www.sogou.com");'
driver.execute_script(js)
time.sleep(1)

# 4:获取当前的窗口列表：
windows_list = driver.window_handles

# 5:切换到0号窗口：
driver.switch_to.window(windows_list[0])
time.sleep(1)
# 6：切换到1号窗口：
driver.switch_to.window(windows_list[1])
time.sleep(1)

driver.quit()
