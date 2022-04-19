from cProfile import label
from lib2to3.pgen2 import driver
from selenium import webdriver
import json
import requests
import ddddocr
import base64
import time
import smtplib
from email.mime.text import MIMEText
from goto import with_goto
# 所有用到的url
login_url = "https://uis.fudan.edu.cn/authserver/login?service=https%3A%2F%2Fzlapp.fudan.edu.cn%2Fa_fudanzlapp%2Fapi%2Fsso%2Findex%3Fredirect%3Dhttps%253A%252F%252Fzlapp.fudan.edu.cn%252Fsite%252Fncov%252FfudanDaily%26from%3Dwap"
get_info_url = "https://zlapp.fudan.edu.cn/ncov/wap/fudan/get-info"
save_url = "https://zlapp.fudan.edu.cn/ncov/wap/fudan/save"
code_url = "https://zlapp.fudan.edu.cn/backend/default/code"
log_file = "C:\\autoDailyFudan\\logging.txt"

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
    receivers = ['19307110250@fudan.edu.cn']  

    #设置email信息
    #邮件内容设置
    message = MIMEText('今日自动打卡于'+'\t'+time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())+'\t'+'成功啦','plain','utf-8')
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

for i in range(5):
    # 打开chrome登陆后获取cookie
    # 静默执行
    option = webdriver.ChromeOptions()
    option.add_argument('headless')
    option.add_argument('verbose')
    option.add_argument('log-path="C:\\Users\\fengchuiyusan\\Desktop\\log.txt"')
    driver = webdriver.Chrome(chrome_options=option)
    driver.get(url=login_url) 

    # 输入账号密码
    username = driver.find_element_by_id("username")
    username.send_keys("19307110250")
    password = driver.find_element_by_id("password")
    password.send_keys("20010331Lyq")

    # 点击登陆
    submitBtn = driver.find_element_by_id("idcheckloginbtn")
    submitBtn.click()

    # 获取cookie
    cookies = driver.get_cookies()
    # print(cookies)
    # 用requests实现下面的操作
    r = requests.Session()
    # r.trust_env = None
    # print(r)
    # 记录cookie
    for cookie in cookies:
        r.cookies.set(cookie['name'],cookie['value'])
    cookie = [item["name"] + "=" + item["value"] for item in cookies ]
    cookiestr = ';'.join(item for item in cookie)

    # 通过接口请求时需要cookies等信息
    headers_cookie ={
        "Cookie": cookiestr         
    }
    print("========================")
    # 获取平安复旦的所有数据
    all_pafd_data = r.get(get_info_url).text
    old_pafd_data = json.loads(all_pafd_data)
    new_pafd_data = old_pafd_data["d"]["info"]
    print(old_pafd_data["d"]["uinfo"]["role"]["number"])

    # 获取验证码图片并识别
    checkin_image_response = requests.get(code_url,headers=headers_cookie)
    base64_bytes = base64.b64encode(checkin_image_response.content)
    checkin_image_base64 = str(base64_bytes,'utf-8')
    ocr = ddddocr.DdddOcr()
    verification_code = ocr.classification(None,checkin_image_base64)
    print(verification_code)

    # 更新要填写的平安复旦信息
    new_pafd_data.update({
        "ismoved": 0,
        "number": old_pafd_data["d"]["uinfo"]["role"]["number"],
        "realname": old_pafd_data["d"]["uinfo"]["realname"],
        "area": old_pafd_data["d"]["oldInfo"]["area"],
        "city": old_pafd_data["d"]["oldInfo"]["city"],
        "province": old_pafd_data["d"]["oldInfo"]["province"],
        "sfhbtl": 0,
        "sfjcgrq": 0,
        "sftgfxcs": 1,
        "sfzx": 1,
        "code": verification_code
    })

    # 提交信息
    response = r.post(save_url, data=new_pafd_data,headers=headers_cookie)

    # 获取提交状态,若验证码错误就重新提交
    submit_status = json.loads(response.text)

    # 书写log
    if new_pafd_data["sfzx"]==1:
        if_in_school = '在校'
    else:
        if_in_school = '不在校'
    with open(log_file,"a") as file:
        file.write('FDU'+'\t'+time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())+'\t'+new_pafd_data["area"]+'\t'+if_in_school+'\t'+submit_status["m"]+'\n')

    # 提示成功
    print(submit_status["m"])
    if submit_status["m"]!="验证码错误":
        driver.close()
        # 成功发送后发送邮件
        if submit_status["m"]=="操作成功":
            send_daily_email()
        break
    