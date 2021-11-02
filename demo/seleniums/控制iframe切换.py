# -*-coding:utf-8-*-
__author__ = 'Administrator'

"""
操作邮箱登录：
1: 先转入iframe内部，填写用户名和密码：
2：然后切换出iframe外部，获取外部的一个元素
"""
import time
from selenium import webdriver

# 转到登录注册页面
driver = webdriver.Chrome()
driver.get("https://mail.qq.com/cgi-bin/loginpage")
time.sleep(2)

# 因为我当前登录了QQ,所以需要先进入iframe，点击账号密码登录
# 1: 定位到iframe标签
login_frame = driver.find_element_by_xpath('//*[@id="login_frame"]')
# 2：跳转到iframe内部
driver.switch_to.frame(login_frame)
time.sleep(2)
# 3: 点击用户名和密码登录：
driver.find_element_by_xpath('//*[@id="switcher_plogin"]').click()
time.sleep(2)
# 4：选中用户名和密码，填写信息
driver.find_element_by_xpath('//*[@id="u"]').send_keys("17852032943@qq.com")
time.sleep(2)
driver.find_element_by_xpath('//*[@id="p"]').send_keys("renshanwenloveyou")
time.sleep(2)

# 5: 切换到iframe外面去：
windows = driver.window_handles
driver.switch_to.window(windows[0])

time.sleep(2)
# 6: 打印登录的标题
content = driver.find_element_by_class_name('login_pictures_title').text
print(content)

driver.quit()
