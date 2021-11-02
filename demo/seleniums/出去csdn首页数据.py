# -*-coding:utf-8-*-
__author__ = 'Administrator'

from selenium import webdriver
import time

driver = webdriver.Chrome()
# 向CSDN发送请求
driver.get("https://www.csdn.net/")
time.sleep(2)

# 1：定位CSDN精选头条：
elements = driver.find_elements_by_class_name('card_title')
# 2: 打印文本信息：
for element in elements:
    print(element.text)
print("--------------------")
# 3：使用Xpath再次获取：
elements = driver.find_elements_by_xpath('//*[@id="floor-choosed-top2_412"]/div/div/div[1]/div[1]/em')
print(elements[0].text)
# 4: 根据文本定位链接信息：
link_element = driver.find_element_by_link_text('Python')
print(link_element.get_attribute("href"))

driver.close()
