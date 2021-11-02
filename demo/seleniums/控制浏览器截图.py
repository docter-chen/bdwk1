# -*-coding:utf-8-*-
__author__ = 'Administrator'

from selenium import webdriver

# 1: 创建浏览器驱动对象
driver = webdriver.Chrome()
# 2: 使用浏览器驱动发送请求：
driver.get("http://www.baidu.com")
# 3： 执行浏览器操作：
# 获取百度的截图
driver.save_screenshot("./百度.png")
# 打印浏览器的标题
print(driver.title)
# 4： 退出浏览器
driver.quit()
