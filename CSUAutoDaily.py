import datetime
from email import message
import time
import json
import re
from lib2to3.pgen2 import driver
from selenium import webdriver
import json
import requests
import smtplib
from email.mime.text import MIMEText
import random

# 所有用到的url
login_url = "https://ca.csu.edu.cn/authserver/login?service=https%3A%2F%2Fwxxy.csu.edu.cn%2Fa_csu%2Fapi%2Fcas%2Findex%3Fredirect%3Dhttps%253A%252F%252Fwxxy.csu.edu.cn%252Fncov%252Fwap%252Fdefault%252Findex%26from%3Dwap"
index_url = "https://wxxy.csu.edu.cn/ncov/wap/default/index"
save_url = 'https://wxxy.csu.edu.cn/ncov/wap/default/save'
log_file = "C:\\autoDailyFudan\\logging.txt"

# 随机情话
def random_love_statement():
    ran_num = random.randint(0,4)
    if ran_num == 0:
        res = "封校了呢,也要记得按时吃饭,多吃青菜鸭  (*^▽^*)"
    elif ran_num == 1:
        res = "好久都没有见臭宝了,想和臭宝贴贴~  o(╥﹏╥)o"
    elif ran_num == 2:
        res = "悄悄告诉你一个秘密:我喜欢你! φ(>ω<*) "
    elif ran_num == 3:
        res = "新的一天开始啦,臭宝开心的不开心的都可以和我分享哦! ヾ(✿ﾟ▽ﾟ)ノ"
    elif ran_num == 4:
        res = "臭宝啵啵~mua~ 哼哼 (๑╹ڡ╹)╭  ♡"
    return res

# 调用发送邮件的方法
def send_daily_email():
    #163邮箱服务器地址
    mail_host = 'smtp.163.com'  
    # #163用户名
    mail_user = 'fushengduobuyu'  
    #密码(部分邮箱为授权码) 
    mail_password = 'QNLTADCLGEDZAQAD'   
    #邮件发送方邮箱地址
    sender = 'fushengduobuyu@163.com'  
    #邮件接受方邮箱地址，注意需要[]包裹，这意味着你可以写多个邮件地址群发
    # receivers = ['8207191619@csu.edu.cn']  
    receivers = ['19307110250@fudan.edu.cn']  
    #邮件内容设置html格式
    mail_content = """
        <html>
            <body>
                <h2 align="center">打卡成功信息记录</h2>
                <hr>
                <h4 align="center">具体打卡信息如下:</h4>
                <hr>
                <table width='100%' align="center" bgcolor="#ecf5ff">
                    <tr padding="5%">
                        <td align="center" padding="10%">打卡时间</td>
                        <td align="center" padding="10%">"""+time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())+"""</td>
                    </tr>
                    <tr padding="5%">
                        <td align="center" padding="10%">打卡地点</td>
                        <td align="center" padding="10%">"""+area+"""</td>
                    </tr>
                    <tr padding="5%">
                        <td align="center" padding="10%">姓名</td>
                        <td align="center" padding="10%">李豫齐</td>
                    </tr padding="5%">
                    <tr padding="5%">
                        <td align="center" padding="10%">是否返校</td>
                        <td align="center" padding="10%">"""+if_go_back_school+"""</td>
                    </tr padding="5%">
                    <tr padding="5%">
                        <td align="center" padding="10%">是否在校</td>
                        <td align="center" padding="10%">"""+if_in_school+"""</td>
                    </tr>
                </table>
                <br>
                <hr>
                <h2 align="center">臭宝乖乖,一起贴贴~</h2>
                <p>"""+random_love_statement()+"""</p>
            </body>
        </html> 
    """
    #设置email信息
    message = MIMEText(mail_content, 'html', 'utf-8')
    #邮件主题       
    message['Subject'] = time.strftime('%Y-%m-%d', time.localtime())+'打卡成功' 
    #发送方信息
    message['From'] = sender
    #接受方信息     
    message['To'] = receivers[0]  

    #登录并发送邮件
    try:
        smtpObj = smtplib.SMTP() 
        #连接到服务器
        smtpObj.connect(mail_host,25)
        #登录到服务器
        smtpObj.login(mail_user,mail_password) 
        #发送
        smtpObj.sendmail(
            sender,receivers,message.as_string()) 
        #退出
        smtpObj.quit() 
        print('success')
    except smtplib.SMTPException as e:
        print('error',e) #打印错误


# 静默执行
option = webdriver.ChromeOptions()
option.add_argument('headless')
driver = webdriver.Chrome(chrome_options=option)
driver.get(url=login_url) 

# 输入账号密码并登录
username = driver.find_element_by_id("username")
username.send_keys("8207191619")
password = driver.find_element_by_id("password")
password.send_keys("qaz1325369")
submitBtn = driver.find_element_by_id("login_submit")
submitBtn.click()

# 获取cookie
cookies = driver.get_cookies()
r = requests.Session()
driver.close()

# 记录cookie
for cookie in cookies:
    r.cookies.set(cookie['name'],cookie['value'])
cookie = [item["name"] + "=" + item["value"] for item in cookies ]
cookiestr = ';'.join(item for item in cookie)

# 通过接口请求时需要cookies等信息
headers_cookie ={
    "Cookie": cookiestr         
}

# 获取前一天的数据
res =r.get(index_url, headers=headers_cookie, verify=False)
html = res.content.decode()
jsontext = re.findall(r'def = {[\s\S]*?};', html)[0]
jsontext = eval(jsontext[jsontext.find("{"):jsontext.rfind(";")].replace(" ", ""))
geo_text = jsontext['geo_api_info']
geo_text = geo_text.replace("false", "False").replace("true", "True")
geo_obj = eval(geo_text)['addressComponent']
area = geo_obj['province'] + " " + geo_obj['city'] + " " + geo_obj['district']
name = re.findall(r'realname: "([^\"]+)",', html)[0]
number = re.findall(r"number: '([^\']+)',", html)[0]
print(area)
# 构造新的数据并查找要发邮件的数据
new_info = jsontext.copy()
if_in_school='是' if new_info['sffx']=='1' else '否'
if_go_back_school='是' if new_info['sffx']=='1' else '否'
new_info['name'] = name
new_info['number'] = number
new_info['area'] = area
today = datetime.date.today()
new_info["date"] = "%4d%02d%02d" % (today.year, today.month, today.day)
new_info["created"] = round(time.time())

# 提交数据
res = r.post(save_url, data=new_info, headers=headers_cookie)
submit_status = json.loads(res.text)

# 发送成功邮件
print(submit_status['m'])
if(submit_status['m']!="操作成功"):
    send_daily_email()