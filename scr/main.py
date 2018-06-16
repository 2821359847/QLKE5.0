# -*- coding: utf-8 -*-

import sys
import threading
from PyQt5 import QtWidgets

from ui.login_ui import Ui_Form_Login
from ui.main_ui import Ui_Form_Main
from PyQt5.QtCore import Qt

from unit import my_request
from unit import my_db

# login 窗口类
class login_window(QtWidgets.QWidget,Ui_Form_Login): 
    def __init__(self):    
        super(login_window,self).__init__()    
        self.setupUi(self)

    # 登陆函数
    def login(self):
        username = self.username_ui.text()
        password = self.password_ui.text()
        if(me_request.login(username, password)):
            self.turn()
        else:
            QtWidgets.QMessageBox.information(self, "Warnning", "登陆数据出错")
    
    # 转移函数
    def turn(self):
        self.hide()
        main_win.show()
        t_init_talbe = threading.Thread(target = main_win.init_table, name='init table')
        t_init_talbe.start()

# main 窗口类
class main_window(QtWidgets.QWidget,Ui_Form_Main):   
    def __init__(self):    
        super(main_window,self).__init__()    
        self.setupUi(self)
        self.queue_count = 0;
        self.queue_count_max = 10;
        self.init_output();
    
    # 初始化 output 
    def init_output(self):
        self.output.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.output.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.output.setText("")
    
    # 初始化 表格数据
    def init_table(self):
        
        self.refresh();
            
        all_course_table = me_db.get()
        size = len(all_course_table)
        self.all_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.all_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.all_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.all_table.setColumnCount(5)
        self.all_table.setRowCount(size)
        self.all_table.setHorizontalHeaderLabels(['课程值','课程号','课程名', '课程组别', '课程余量'])
        
        for i in range(size):
            course_value = QtWidgets.QTableWidgetItem(all_course_table[i][1])
            self.all_table.setItem(i, 0, course_value)
            course_id = QtWidgets.QTableWidgetItem(all_course_table[i][2])
            self.all_table.setItem(i, 1, course_id)
            course_name = QtWidgets.QTableWidgetItem(all_course_table[i][3])
            self.all_table.setItem(i, 2, course_name)
            course_group = QtWidgets.QTableWidgetItem(all_course_table[i][4])
            self.all_table.setItem(i, 3, course_group)
            course_remain = QtWidgets.QTableWidgetItem(all_course_table[i][5])
            self.all_table.setItem(i, 4, course_remain)
            
        self.result_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.result_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.result_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.result_table.setColumnCount(5)
        self.result_table.setHorizontalHeaderLabels(['课程值','课程号','课程名', '课程组别', '课程余量'])
        
        self.list_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.list_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.list_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.list_table.setColumnCount(3)
        self.list_table.setRowCount(self.queue_count_max)
        self.list_table.setHorizontalHeaderLabels(['课程值', '课程号', '课程序号'])
    
    # 搜索 课程号
    def search(self):
        self.me_print('搜索中')
        result_course = me_db.search(self.search_line.text())
        size = len(result_course)
        self.result_table.setRowCount(size)
        for i in range(size):
            class_value = QtWidgets.QTableWidgetItem(result_course[i][1])
            self.result_table.setItem(i, 0, class_value)
            class_id = QtWidgets.QTableWidgetItem(result_course[i][2])
            self.result_table.setItem(i, 1, class_id)
            class_name = QtWidgets.QTableWidgetItem(result_course[i][3])
            self.result_table.setItem(i, 2, class_name)
            class_group = QtWidgets.QTableWidgetItem(result_course[i][4])
            self.result_table.setItem(i, 3, class_group)
            class_left = QtWidgets.QTableWidgetItem(result_course[i][5])
            self.result_table.setItem(i, 4, class_left)
        self.me_print('    获取到课程' + str(size))
        return size
        
    def en_queue(self, int_row, int_col):
        self.me_print('添加待选项')
        tmp = me_db.get()[int_row]
        self.me_print('    ' + tmp[3])
        if(self.queue_count < self.queue_count_max):
            if(me_request.en_to_courses_table(tmp)):
                course_value = QtWidgets.QTableWidgetItem(tmp[1])
                self.list_table.setItem(self.queue_count, 0, course_value)
                course_id = QtWidgets.QTableWidgetItem(tmp[2])
                self.list_table.setItem(self.queue_count, 1, course_id)
                course_idx = QtWidgets.QTableWidgetItem(tmp[3].split(' ', 1)[1])
                self.list_table.setItem(self.queue_count, 2, course_idx)
                
                self.queue_count = self.queue_count + 1
                return True
            else:
                self.me_print('    添加待选项重复')
        else:
            self.me_print('    添加待选项失败')
            QtWidgets.QMessageBox.information(self, "Warnning", "超出列表范围")
        return False
        
    def refresh_queue(self):
        self.me_print('重新获取待选项')
        queue_list = me_request.to_courses_talbe;
        size = len(queue_list)
        for i in range(size):
            class_value = QtWidgets.QTableWidgetItem(queue_list[i][0])
            self.list_table.setItem(i, 0, class_value)
            class_kch = QtWidgets.QTableWidgetItem(queue_list[i][1])
            self.list_table.setItem(i, 1, class_kch)
            class_kxh = QtWidgets.QTableWidgetItem(queue_list[i][2])
            self.list_table.setItem(i, 2, class_kxh)
            
        for i in range(size, self.queue_count_max):
            blank1 = QtWidgets.QTableWidgetItem('')
            self.list_table.setItem(i, 0, blank1)
            blank2 = QtWidgets.QTableWidgetItem('')
            self.list_table.setItem(i, 1, blank2)
            blank3 = QtWidgets.QTableWidgetItem('')
            self.list_table.setItem(i, 2, blank3)
        self.me_print('    获取到课程' + str(size))
        self.queue_count = size;
    
    def out_queue(self, int_x, int_y):
        self.me_print("删除待选项")
        self.list_table.removeRow(int_x);
        self.list_table.setRowCount(10)
        self.queue_count = self.queue_count - 1
        pop_item = me_request.to_courses_talbe.pop(int_x)
        self.me_print('    ' + pop_item[3])
        return pop_item
        
    def refresh(self):
        self.me_print("重新获取已选课程")
        size = me_request.get_had_course_count();
        had_courses_table = me_request.had_courses_table;
        
        self.had_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.had_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.had_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.had_table.setColumnCount(3)
        self.had_table.setRowCount(size)
        self.had_table.setHorizontalHeaderLabels(['课程号','课程', '状态'])
        
        for i in range(size):
            course_id = QtWidgets.QTableWidgetItem(had_courses_table[i][0])
            self.had_table.setItem(i, 0, course_id)
            course_name = QtWidgets.QTableWidgetItem(had_courses_table[i][1])
            self.had_table.setItem(i, 1, course_name)
            course_statue = QtWidgets.QTableWidgetItem(had_courses_table[i][2])
            self.had_table.setItem(i, 2, course_statue)
            
        self.me_print('    获取到课程' + str(size));
        return size
        
    def begin(self):
        self.me_print('强课开始')
        t2_init_talbe = threading.Thread(target = me_request.main, args=(self.me_print,self.refresh_queue), name='to_main')
        t2_init_talbe.start()
    
    def re_remain(self):
        self.me_print('重新拉去剩余数据')
    
    # 从搜索列表 入队
    def en_queue2(self, int_row, int_col):
        self.me_print('添加待选项')
        tmp = me_db.result[int_row]
        self.me_print('    ' + tmp[3])
        if(self.queue_count < self.queue_count_max):
            if(me_request.en_to_courses_table(tmp)):
                course_value = QtWidgets.QTableWidgetItem(tmp[1])
                self.list_table.setItem(self.queue_count, 0, course_value)
                course_id = QtWidgets.QTableWidgetItem(tmp[2])
                self.list_table.setItem(self.queue_count, 1, course_id)
                course_idx = QtWidgets.QTableWidgetItem(tmp[3].split(' ', 1)[1])
                self.list_table.setItem(self.queue_count, 2, course_idx)
                
                self.queue_count = self.queue_count + 1
            else:
                self.me_print('    添加待选项重复')
        else:
            self.me_print('    添加待选项失败')
            QtWidgets.QMessageBox.information(self, "Warnning", "超出列表范围")
            
    def stop(self):
        self.me_print('stop');
    
    # 日志打印函数
    def me_print(self, tmp_str):
        tmp_str = str(tmp_str)
        self.output.append(tmp_str)
    
    # 关闭退出
    def closeEvent(self, event):
        reply = QtWidgets.QMessageBox.question(self, '警告', '退出后测试将停止,\n你确认要退出吗？',QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            me_request.logout()
            event.accept()
        else:
            event.ignore()
        

if  __name__ == "__main__":
    
    me_request = my_request()
    me_db = my_db()
    
    app = QtWidgets.QApplication(sys.argv)
    app.aboutToQuit.connect(app.deleteLater)
    
    login_win = login_window()
    main_win = main_window()
    
    login_win.show()
    main_win.hide()
    
sys.exit(app.exec_())