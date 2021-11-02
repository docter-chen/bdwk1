# -*-coding:utf-8-*-
__author__ = 'Administrator'

from selenium import webdriver

driver = webdriver.PhantomJS()
driver.get("http://www.baidu.com")
driver.save_screenshot("./百度.png")
driver.quit()
