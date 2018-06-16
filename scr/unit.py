# -*- coding: utf-8 -*-

import time
import requests
import smtplib
import numpy as np
from bs4 import BeautifulSoup
from pymongo import MongoClient
from email.mime.text import MIMEText

class my_request:
    def __init__(self):
        self.page_num = 43
        self.r_session = requests.session()
        self.error_count = 0
        self.had_courses_table = []
        self.all_courses_table = []
        self.to_courses_talbe = []
        self._username = ''
        self._password = ''
        self.my_courses_count = 0;
        self.me_mail = my_mail();
        
    # 解码函数
    def decode_html(self, text):
        try:
            result = text.decode()
        except:
            try:
                result = text.decode('gbk')
            except:
                print('读不懂')
                result = ''
        return result
    
    # 登陆函数
    def login(self, username, password):
        self._username = username
        self._password = password
        headers = {
            'Host':"jwc.bjtu.edu.cn",
            'Accept-Language':"zh-CN,zh;q=0.9",
            'Accept-Encoding':"gzip, deflate",
            'Connection':"keep-alive",
            'Referer':"http://jwc.bjtu.edu.cn/index.html",
            'User-Agent':"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36"
        }
        data = {
            "username" : username,
            "password" : password,
            "type"     : "1",
            "_"        : ""
        }
        try:
            page = self.r_session.get('http://jwc.bjtu.edu.cn/login_introduce_s.html', timeout = 1)
            page = self.r_session.get("http://jwc.bjtu.edu.cn:82/LoginAjax.aspx?", data=data, headers=headers, timeout = 1)
            res = self.decode_html(page.content)
            print(res)
            page = self.r_session.get('http://jwc.bjtu.edu.cn:82/NoMasterJumpPage.aspx?URL=jwcNjwStu&amp;FPC=page:jwcNjwStu', timeout = 1)
            if(res[12] == '1'):
                self.my_courses_count = self.get_had_course_count();
                return True
        except:
            print('error in login')
        return 0
    
    # 登出
    def logout(self):
        try:
            self.r_session.get('https://dean.bjtu.edu.cn/client/logout/');
        except:
            print('logout 失败')
        
    # 重新登陆函数
    def relogin(self):
        return(self.login(self._username, self._password))
    
    # 获取已有课程信息
    def get_had_course(self):
        self.had_courses_table = [];
        page = self.r_session.get('https://dean.bjtu.edu.cn/course_selection/courseselecttask/schedule/', timeout = 1);
        soup = BeautifulSoup(page.content,"html5lib");
        table = soup.find_all('table')[1];
        trs = table.find_all('tr');
        for i in np.arange(1, len(trs)):
            tds = trs[i].find_all('td');
            if(tds[6].text != '未中'):
                tmp = tds[1].text.replace('\n', ' ').replace('  ', '').split(' ', 1);
                self.had_courses_table.append([tmp[0], tmp[1], tds[6].text]);
        return self.had_courses_table;
    
    # 获取已选课数量
    def get_had_course_count(self):
        return(len(self.get_had_course()));
    
    # 获取所有课程信息
    def get_all_class(self):
        for i in np.arange(1, self.page_num + 1):
            data = {
                'action':'load',
                'iframe':'school',
                'page':i
            };
            try:
                page = self.r_session.get('https://dean.bjtu.edu.cn/course_selection/courseselecttask/selects_action/', params=data);
                soup = BeautifulSoup(page.content,"html5lib");
                table = soup.find_all('table')[0];
                trs = table.find_all('tr');
                for i in np.arange(1, len(trs)):
                    tds = trs[i].find_all('td');
                    tmp = ['', '', '', '', ''];
                    try:
                        tmp[0] = tds[0].find('input').attrs['value'];
                    except:
                        tmp[0] = tds[0].text.replace('\n', '').replace(' ', '');
                    tmp[1] = tds[2].text.split('】', 1)[0].split('【', 1)[1];
                    tmp[2] = tds[2].text.split('】', 1)[1];
                    tmp[3] = tds[4].text;
                    tmp[4] = str(int(tds[5].text));
                    self.all_course_table.append(tmp);
            except:
                print('获取所由课程出错');
        return self.all_course_table;
    
    # post 函数
    def my_post(self, value):
        header = {
            'action':'submit'
        };
        body = {
            'checkboxs':value
        };
        try:
            page = self.r_session.post('https://dean.bjtu.edu.cn/course_selection/courseselecttask/selects_action/', params=header, data = body, timeout = 1);
        except:
            self.my_post();
            print('选课 post 出现问题');
            self.error_count = self.error_count + 1;
        return page.status_code;
    
    # 搜索函数, kxh = '00', 找到有课的, kxh = '0x', 返回是否有课
    def remain(self, kch, kxh):
        data = {
            'kkxsh': '',
            'kch': kch,
            'jsh':'',
            'skxq':'',
            'skjc':'',
            'has_advance_query':'1'
        };
        try:
            page = self.r_session.get('https://dean.bjtu.edu.cn/course_selection/courseselecttask/remains/', params=data, timeout = 1);
            soup = BeautifulSoup(page.content,"html5lib");
            table = soup.find_all('table')[0];
            trs = table.find_all('tr');
            if(kxh == '00'):      
                for i in np.arange(1, len(trs)):
                    tds = trs[i].find_all('td');
                    if(int(tds[4].text) != 0):
                        print(tds[1].text);
                        print(tds[4].text);
                return True;
            else :
                for i in np.arange(1, len(trs)):
                    tds = trs[i].find_all('td');
                    tmp_str = tds[1].text.split(' ', 3)[2];
                    if(tmp_str == kxh + '\n'):
                        if(int(tds[4].text) != 0):
                            return True;
        except:
            print('搜索时出现错误');
            self.error_count = self.error_count + 1;
        return False;
    
    # 抢课循环
    def loop_main(self, me_print, value, kch, kxh):
        count = 1;
        while(True):
            if(self.error_count < 10):
                me_print('    搜索次数' + str(count))
                time.sleep(0.5);
                if(self.remain(kch, kxh)):
                    self.my_post(value)
                    if(self.get_had_course_count() > self.my_courses_count):
                        self.me_mail.send('选课成功', '恭喜')
                        me_print('选课成功' + kch)
                        return True
                count = count+1
            else:
                self.relogin()
                self.error_count = 0
        return False;
    
    def main(self, me_print, me_refresh):
        size = len(self.to_courses_talbe)
        count = 1;
        k = 0
        while(size > 0):
            if(self.error_count < 10):
                me_print('    搜索次数' + str(count))
                time.sleep(0.5);
                if(self.remain(self.to_courses_talbe[k][1], self.to_courses_talbe[k][2])):
                    self.my_post(self.to_courses_talbe[k][0])
                    if(self.get_had_course_count() > self.my_courses_count):
                        self.me_mail.send('选课成功', '恭喜')
                        me_print('选课成功' + self.to_courses_talbe[k][1])
                        self.to_courses_talbe.pop(k)
                        me_refresh()
                        size = len(self.to_courses_talbe)
                        k = size
                        self.my_courses_count = self.get_had_course_count();
                k = k + 1
                if(k >= size):
                    k = 0
                count = count+1
            else:
                self.relogin()
                self.error_count = 0
        return False;
    
    
    def en_to_courses_table(self, tmp_list):
        if(tmp_list[1] != "无余量" and tmp_list[1] != "已选"):
            for i in range(len(self.to_courses_talbe)):
                if(self.to_courses_talbe[i][1] == tmp_list[1]):
                    return False
            self.to_courses_talbe.append([tmp_list[1], tmp_list[2], tmp_list[3].split(' ', 1)[1]])
            return True


class my_db:
    def __init__(self):
        self.infos = [];
        self.result = [];
        self.client = MongoClient('localhost',27017);
        self.db = self.client.QLKE;
        self.course = self.db.course;
        self.infos = self.read();
        
    # 初次 获取 mongo 里的数据
    def read(self):
        documents = self.course.find();
        for i in documents:
            self.infos.append(list(i.values()));
        return self.infos;
    
    # 直接拿到数据
    def get(self):
        return self.infos;
    
    # 更新 mongo 里的数据
    def updata(self, me_request):
        all_class_table = me_request.all_class();
        for i in all_class_table():
            self.course.update_one({"name":i[1]},{"$set":{"remain":i[3]}});
        return True;
        
    # 查找 mongo 里的数据
    def search(self, id_str):
        self.result = [];
        documents = self.course.find({"id":id_str});
        for i in documents:
            self.result.append(list(i.values()));
        return self.result;
        
        
class my_mail:
    def __init__(self):
        print('mail init')
        
    def send(self, content, title):
        # 第三方 smtp 服务信息
        mail_host="smtp.163.com";  #设置服务器
        mail_user="mepython";    #用户名
        mail_pass="pythonME0";   #口令 
        
        sender = 'mepython@163.com';
        receivers = ['16301156@bjtu.edu.cn'];
        
        message = MIMEText(content, 'plain', 'utf-8');
        message['From'] = "{}".format(sender);
        message['To'] =  ",".join(receivers);
        message['Subject'] = title;
        try:
            server=smtplib.SMTP_SSL(mail_host, 465, timeout=5);
            server.login(mail_user,mail_pass);
            server.sendmail(sender, receivers, message.as_string());
            print ("Success: 邮件发送成功");
        except smtplib.SMTPException:
            print ("Error: 无法发送邮件");
            self.send(content, title);
        finally:
            server.close();
        return True;
        
                     