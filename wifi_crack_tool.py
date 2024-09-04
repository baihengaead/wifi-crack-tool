# -*- coding: UTF-8 -*-
"""
Author: 白恒aead
Repositories: https://github.com/baihengaead/wifi-crack-tool
Version: 1.2.3
"""
import os,sys,datetime,time,threading,ctypes,json
import platform

from pywifi import const,PyWiFi,_wifiutil_win,Profile
from pywifi.iface import Interface

import pyperclip

from PySide6.QtCore import Qt, QThread, Signal, QSize
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QWidget, QMessageBox
from PySide6.QtGui import QIcon
from wifi_crack_tool_gui import Ui_MainWindow

class MainWindow(QMainWindow):
    def __init__(self,mutex):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.icon_path = ""
        if getattr(sys, 'frozen', False):
            self.icon_path = os.path.join(sys._MEIPASS, "images/wificrack.ico") # type: ignore
        else:
            self.icon_path = "images/wificrack.ico"
        
        if PyWiFi().interfaces().__len__() <= 1 and  mutex is None:
            self.showinfo(title=self.windowTitle(), message='应用程序的另一个实例已经在运行。')
            sys.exit()
        
        icon = QIcon()
        icon.addFile(self.icon_path, QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.setWindowIcon(icon)
        
        #------------------------- 初始化控件状态 -------------------------------#
        self.ui.cbo_wifi_name.addItem('——全部——')
        
        self.ui.cbo_security_type.addItems(['——自动——','WPA','WPAPSK','WPA2','WPA2PSK','WPA3','WPA3SAE','OPEN'])
        self.ui.cbo_security_type.setCurrentIndex(0)
        self.set_display_using_pwd_file()
        
        self.ui.cbo_wifi_name.setDisabled(True)
        self.ui.cbo_wnic.setDisabled(True)
        self.ui.btn_refresh_wifi.setDisabled(True)
        self.ui.btn_start.setDisabled(True)
        self.ui.btn_stop.setDisabled(True)
        
        self.ui.txt_log_msg_info.setReadOnly(True)
        self.log_end = self.ui.txt_log_msg_info.textCursor().MoveOperation.End
        self.log_color = self.ui.txt_log_msg_info.textColor()
        #======================================================================#
        
        self.tool = WifiCrackTool(self)
        #---------------------- 绑定事件 ---------------------------#
        self.ui.btn_change_pwd_file.clicked.connect(self.tool.change_pwd_file)
        self.ui.btn_refresh_wifi.clicked.connect(self.tool.refresh_wifi)
        self.ui.btn_start.clicked.connect(self.tool.start)
        self.ui.btn_stop.clicked.connect(self.tool.stop)
        self.ui.dbl_scan_time.valueChanged.connect(self.tool.change_scan_time)
        self.ui.dbl_connect_time.valueChanged.connect(self.tool.change_connect_time)
        #===========================================================#
        
        #---------------------- 更新GUI的信号对象 -------------------------#
        self.show_msg = MainWindow.SignThread(self.ui.centralwidget,self.tool.show_msg,str,str)
        self.clear_msg = MainWindow.SignThread(self.ui.centralwidget,self.tool.clear_msg)
        self.add_wifi_items = MainWindow.SignThread(self.ui.centralwidget,self.ui.cbo_wifi_name.addItems,list)
        self.set_wifi_current_index = MainWindow.SignThread(self.ui.centralwidget,self.ui.cbo_wifi_name.setCurrentIndex,int)
        self.set_control_state = MainWindow.SignThread(self.ui.centralwidget,self.set_control_enabled,bool,QWidget)
        self.reset_controls_state = MainWindow.SignThread(self.ui.centralwidget,self.tool.reset_controls_state)
        self.set_controls_running_state = MainWindow.SignThread(self.ui.centralwidget,self.tool.set_controls_running_state)
        self.show_info = MainWindow.SignThread(self.ui.centralwidget,self.showinfo,str,str)
        self.show_warning = MainWindow.SignThread(self.ui.centralwidget,self.showwarning,str,str)
        self.show_error = MainWindow.SignThread(self.ui.centralwidget,self.showerror,str,str)
        #=================================================================#
        
        self.show_msg.send(f"初始化完成！\n","black")
    
    def showinfo(self,title:str,message:str):
        '''
        显示消息提示框
        
        :title 提示框标题
        :message 提示框文本
        '''
        # 创建QMessageBox实例
        msg_box = QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setWindowIcon(QIcon(self.icon_path))
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        # 设置窗口标志，使其始终置顶
        msg_box.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        # 显示消息框
        msg_box.exec()
    
    def showwarning(self,title:str,message:str):
        '''
        显示警告提示框
        
        :title 提示框标题
        :message 提示框文本
        '''
        # 创建QMessageBox实例
        msg_box = QMessageBox(self.ui.centralwidget)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setWindowIcon(QIcon(self.icon_path))
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        # 设置窗口标志，使其始终置顶
        msg_box.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        # 显示消息框
        msg_box.exec()
    
    def showerror(self,title:str,message:str):
        '''
        显示错误提示框
        
        :title 提示框标题
        :message 提示框文本
        '''
        # 创建QMessageBox实例
        msg_box = QMessageBox(self.ui.centralwidget)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setWindowIcon(QIcon(self.icon_path))
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        # 设置窗口标志，使其始终置顶
        msg_box.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        # 显示消息框
        msg_box.exec()
    
    def set_display_using_pwd_file(self,filename:str="(无)"):
        self.ui.lbl_using_pwd_file.setText(f"正在使用密码本：{filename}")
    
    def set_control_enabled(self,state:bool,*control:QWidget):
        '''
        设置控件启用
        
        :state True->启用，False->禁用
        :control 控件对象
        '''
        if len(control) > 1:
            for con in control:
                con.setEnabled(state)
        elif len(control) == 1:
            control[0].setEnabled(state)
        
    class SignThread(QThread):
        """GUI信号线程"""
    
        def __new__(cls, parent: QWidget, func, *types: type):
            cls.__update_date = Signal(*types, name=func.__name__)  # 定义信号(*types)一个信号中可以有一个或多个类型的数据(int,str,list,...)
            return super().__new__(cls)  # 使用父类__new__方法创建SignThread实例对象
    
        def __init__(self, parent: QWidget, func, *types: type):
            """
            GUI信号线程初始化\n
            :param parent: 界面UI控件
            :param func: 信号要绑定的方法
            :param types: 信号类型,可以是一个或多个(type,...)
            """
            super().__init__(parent)  # 初始化父类
            self.__update_date.connect(func)  # 绑定信号与方法
    
        def send(self, *args):
            """
            向GUI线程发送更新信号\n
            :param args: 信号的内容
            :return:
            """
            self.__update_date.emit(*args)  # 发送信号元组(type,...)

class WifiCrackTool:
    def __init__(self,win:MainWindow):
        self.win = win
        self.ui = win.ui
        
        self.config_dir_path = os.getcwd()+"/config" #配置文件目录路径
        # 如果不存在config目录，则创建
        if not os.path.exists(self.config_dir_path):
            os.mkdir(self.config_dir_path)

        self.log_dir_path = os.getcwd()+"/log" #日志目录路径
        # 如果不存在log目录，则创建
        if not os.path.exists(self.log_dir_path):
            os.mkdir(self.log_dir_path)
        
        self.dict_dir_path = os.getcwd()+"/dict" #字典目录路径
        # 如果不存在dict目录，则创建
        if not os.path.exists(self.dict_dir_path):
            os.mkdir(self.dict_dir_path)

        self.config_file_path = self.config_dir_path+'/settings.json'
        self.config_settings_data = {
            'scan_time':8,
            'connect_time':3,
            'pwd_txt_path':'passwords.txt'
        }
        if os.path.exists(self.config_file_path):
            with open(self.config_file_path, 'r',encoding='utf-8') as config_file:
                self.config_settings_data = json.load(config_file)
                self.ui.dbl_scan_time.setValue(self.config_settings_data['scan_time'])
                self.ui.dbl_connect_time.setValue(self.config_settings_data['connect_time'])
        else:
            with open(self.config_file_path, 'w',encoding='utf-8') as config_file:
                json.dump(self.config_settings_data, config_file, indent=4)
        
        pwd_txt_paths = self.config_settings_data['pwd_txt_path'].split('/')
        self.pwd_txt_name = pwd_txt_paths[len(pwd_txt_paths)-1]
        
        self.pwd_dict_path = self.dict_dir_path+'/pwdict.json'
        
        self.pwd_dict_data:list[dict[str,str]] = []
        if os.path.exists(self.pwd_dict_path):
            # 读取密码字典数据
            with open(self.pwd_dict_path, 'r',encoding='utf-8') as json_file:
                self.pwd_dict_data = json.load(json_file)

        self.run = False
        self.pwd_file_changed = False
        
        # 创建破解对象
        self.crack = self.Crack(self)
        
        # 判断默认密码本是否存在
        if not os.path.exists(self.config_settings_data['pwd_txt_path']):
            self.win.showwarning(title='警告', message='默认密码本[%s]不存在！\n请选择密码本'%(self.config_settings_data['pwd_txt_path']))
            self.config_settings_data['pwd_txt_path'] = ""
            self.change_pwd_file()
        else:
            self.win.set_display_using_pwd_file(self.pwd_txt_name)
    
    # 修改扫描WiFi时间
    def change_scan_time(self):
        self.win.tool.config_settings_data['scan_time'] = self.ui.dbl_scan_time.value()
    
    # 修改连接WiFi时间
    def change_connect_time(self):
        self.win.tool.config_settings_data['connect_time'] = self.ui.dbl_connect_time.value()
    
    # 选择密码本
    def change_pwd_file(self):
        '''选择密码本'''

        try:
            default_dir = r"."
            temp_file_path,_ = QFileDialog.getOpenFileName(self.win, caption=u'选择密码本', dir=(os.path.expanduser(default_dir)), filter="Text files (*.txt);;JSON files (*.json)")
            temp_filepaths = temp_file_path.split('/')
            temp_filename = temp_filepaths[len(temp_filepaths)-1]
            temp_filenames = temp_filename.split('.')
            temp_filetype = temp_filenames[len(temp_filenames)-1]
            if(temp_filetype==''):
                self.win.showinfo(title='提示',message='未选择密码本')
                self.pwd_file_changed = False
            elif(temp_filetype not in ['txt','json']):
                self.win.showerror(title='选择密码本',message='密码本类型错误！\n目前仅支持格式为[txt]的密码本和[json]的密码字典\n您选择的密码本格式为['+temp_filetype+']')
                self.pwd_file_changed = False
            else:
                self.config_settings_data['pwd_txt_path'] = temp_file_path
                self.pwd_txt_paths = temp_filepaths
                self.pwd_txt_name = temp_filename
                self.win.set_display_using_pwd_file(self.pwd_txt_name)
                self.pwd_file_changed = True
        except Exception as r:
            self.win.showerror(title='错误警告',message='选择密码本时发生未知错误 %s' %(r))

    # 显示日志消息
    def show_msg(self,msg:str,color:str="black"):
        '''显示日志消息'''
        dt = datetime.datetime.now()
        with open(f"{self.log_dir_path}/wifi_crack_log_{dt.strftime('%Y%m%d')}.txt","a",encoding='utf-8') as log:
            log.write(dt.strftime('%Y-%m-%d %H:%M:%S')+" >> "+msg)#输出日志到本地文件
        self.ui.txt_log_msg_info.moveCursor(self.win.log_end)
        self.ui.txt_log_msg_info.insertHtml("<span style='color:"+color+";'>"+dt.strftime('%Y-%m-%d %H:%M:%S')+" >> "+msg.replace('\n', '<br/>')+"</span><br/>")
        self.ui.txt_log_msg_info.moveCursor(self.win.log_end)

    # 清空日志消息
    def clear_msg(self):
        '''清空输出消息'''
        self.ui.txt_log_msg_info.setPlainText("")

    # 重置所有控件状态
    def reset_controls_state(self):
        '''重置状态'''
        self.ui.cbo_wifi_name.setEnabled(True)
        self.ui.cbo_security_type.setEnabled(True)
        self.ui.cbo_wnic.setEnabled(True)
        self.ui.dbl_scan_time.setEnabled(True)
        self.ui.dbl_connect_time.setEnabled(True)
        self.ui.btn_change_pwd_file.setEnabled(True)
        self.ui.btn_refresh_wifi.setEnabled(True)
        self.ui.btn_start.setEnabled(True)
        self.ui.btn_stop.setDisabled(True)
    
    # 设置所有控件为运行时的状态
    def set_controls_running_state(self):
        '''运行状态'''
        self.ui.cbo_wifi_name.setDisabled(True)
        self.ui.cbo_security_type.setDisabled(True)
        self.ui.cbo_wnic.setDisabled(True)
        self.ui.dbl_scan_time.setDisabled(True)
        self.ui.dbl_connect_time.setDisabled(True)
        self.ui.btn_change_pwd_file.setDisabled(True)
        self.ui.btn_refresh_wifi.setDisabled(True)
        self.ui.btn_start.setDisabled(True)
        self.ui.btn_stop.setEnabled(True)
    
    # 刷新wifi列表
    def refresh_wifi(self):
        try:
            self.ui.cbo_wifi_name.clear()
            self.ui.cbo_wifi_name.addItem('——全部——')
            self.ui.cbo_wifi_name.setDisabled(True)
            self.ui.btn_refresh_wifi.setDisabled(True)
            self.ui.btn_start.setDisabled(True)
            self.ui.cbo_wnic.setDisabled(True)
            self.ui.dbl_scan_time.setDisabled(True)
            thread = threading.Thread(target=self.crack.search_wifi,args=())
            thread.daemon = True
            thread.start()
        except Exception as r:
            self.win.showerror(title='错误警告',message='扫描wifi时发生未知错误 %s' %(r))
            self.show_msg('扫描wifi时发生未知错误 %s\n\n' %(r),"red")
            self.reset_controls_state()

    # 开始暴力破解
    def start(self):
        try:
            if self.config_settings_data['pwd_txt_path']!="" and os.path.exists(self.config_settings_data['pwd_txt_path']):
                wifi_name = self.ui.cbo_wifi_name.currentText()
                self.run = True
                self.set_controls_running_state()
                if self.ui.cbo_wifi_name.currentIndex() == 0:
                    thread = threading.Thread(target=self.crack.auto_crack)
                    thread.daemon = True
                    thread.start()
                else:
                    thread = threading.Thread(target=self.crack.crack,args=(wifi_name,))
                    thread.daemon = True
                    thread.start()
            else:
                if self.change_pwd_file():
                    self.start()
        except Exception as r:
            self.win.showerror(title='错误警告',message='开始运行时发生未知错误 %s' %(r))
            self.show_msg('开始运行时发生未知错误 %s\n\n' %(r),"red")
            self.reset_controls_state()

    # 终止暴力破解
    def stop(self):
        try:
            self.run = False
            self.show_msg("正在尝试终止破解...")
        except Exception as r:
            self.win.showerror(title='错误警告',message='停止时发生未知错误 %s' %(r))
            self.show_msg('停止时发生未知错误 %s\n\n' %(r),"red")
            self.reset_controls_state()

    # 暴力破解wifi密码的类
    class Crack:
        '''用于暴力破解wifi的类'''
        def __init__(self,tool:'WifiCrackTool'):
            self.tool:WifiCrackTool = tool
            self.win = tool.win
            self.ui = tool.ui
            self.wifi = PyWiFi()
            self.wnics = self.wifi.interfaces()
            self.iface:Interface
            self.get_wnic()
            self.ssids = []
            self.profile_dict = {}
            '''wifi信息字典'''
            self.convert_success = False
            self.is_auto = False

        def coding_convert(self,content:str,encoding:str='utf-8'):
            try:
                return content.encode('raw_unicode_escape').decode(encoding)
            except Exception as r:
                self.win.show_msg.send(f"编码转换时发生错误 {r}\n\n","red")
                self.win.reset_controls_state.send()
                return False
        
        def get_wnic(self):
            '''获取无线网卡'''
            try:
                if self.wnics.__len__() > 0:
                    self.tool.show_msg(f'已搜索到无线网卡（数量:{self.wnics.__len__()}）\n')
                    for i,wnic in enumerate(self.wnics):
                        self.ui.cbo_wnic.addItem(wnic.name(),i)
                    self.ui.cbo_wnic.setEnabled(True)
                    self.ui.btn_refresh_wifi.setEnabled(True)
                else:
                    self.win.showwarning(title='警告',message='无法获取到无线网卡！\n请确保你的电脑拥有无线网卡再继续使用。')
                    self.tool.show_msg('无法获取到无线网卡！\n请确保你的电脑拥有无线网卡才可继续使用。\n\n')
                
            except Exception as r:
                self.win.showerror(title='错误警告',message=f'获取无线网卡时发生未知错误 {r}')
                self.tool.show_msg(f"获取无线网卡时发生未知错误 {r}\n\n","red")
                self.tool.reset_controls_state()
                
        def search_wifi(self):
            """扫描附近wifi => wifi名称数组"""
            try:
                self.iface = self.wnics[self.ui.cbo_wnic.currentData()]
                name = self.iface.name()#网卡名称
                self.iface.scan()#扫描AP
                self.win.show_msg.send(f"正在使用网卡[{name}]扫描WiFi...\n","black")
                time.sleep(self.tool.config_settings_data['scan_time']) # 由于不同网卡的扫描时长不同，建议调整合适的延时时间
                ap_list = self.iface.scan_results()#扫描结果列表
                
                # 去除重复AP项
                ap_dic_tmp = {}
                for b in ap_list:
                    if b.ssid.replace(' ', '') != '':
                        ap_dic_tmp[b.ssid] = b
                
                # 将字典转换为列表，并去除列表中的空字符项
                ap_list = list(ap_dic_tmp.values())
                
                self.win.show_msg.send("扫描完成！\n","black")
                self.ssids:list[str] = []
                self.profile_dict:dict[str,Profile] = {}
                for i,data in enumerate(ap_list):#输出扫描到的WiFi名称
                    ssid = data.ssid
                    self.ssids.insert(i,ssid)
                    profile = Profile()
                    profile.ssid = data.ssid # * wifi名称
                    profile.auth = data.auth # * 网卡的开放
                    profile.akm = data.akm # * wifi加密算法，一般是 WPA2PSK
                    profile.cipher = data.cipher # * 加密单元
                    self.profile_dict[data.ssid] = profile
                self.win.reset_controls_state.send()
                self.win.add_wifi_items.send(self.ssids)
                if len(self.ssids) > 0:
                    self.win.set_wifi_current_index.send(0)
            except Exception as r:
                self.win.show_error.send('错误警告',f'扫描wifi时发生未知错误 {r}')
                self.win.show_msg.send(f"扫描wifi时发生未知错误 {r}\n\n","red")
                self.win.reset_controls_state.send()

        def auto_crack(self):
            '''
            自动破解所有WiFi
            '''
            try:
                self.is_auto = True
                self.win.show_msg.send(f"开始自动破解已扫描到的所有WiFi\n","blue")
                wifi_info = "WiFi列表：\n"
                for i,ssid in enumerate(self.ssids,1):
                    wifi_info = wifi_info+f"{('&nbsp;'*40)}({i}){('&nbsp;'*10)}{ssid}\n"
                self.win.show_msg.send(wifi_info,"blue")
                
                pwds = {}
                colors = {}
                for ssid in self.ssids:
                    pwd = self.crack(ssid)
                    if isinstance(pwd,str):
                        pwds[ssid] = pwd
                        colors[ssid] = "green"
                    else:
                        pwds[ssid] = "破解失败"
                        colors[ssid] = "red"
                
                self.win.show_msg.send(f"自动破解已完成！\n","blue")
                crack_result_info = "结果如下：\n"
                for i,ssid in enumerate(self.ssids,1):
                    crack_result_info = crack_result_info+f"<span style='color:{colors[ssid]}'>{('&nbsp;'*40)}({i}){('&nbsp;'*10)}{ssid}{('&nbsp;'*10)}{pwds[ssid]}</span>\n"
                
                self.win.show_msg.send(crack_result_info,"blue")
                self.win.show_info.send('自动破解',"自动破解已完成！破解结果已记录到日志中")
                
                self.is_auto = False
                self.tool.reset_controls_state()
            except Exception as r:
                self.win.show_error.send('错误警告','自动破解过程中发生未知错误 %s' %(r))
                self.win.show_msg.send(f"自动破解过程中发生未知错误 {r}\n\n","red")
                self.is_auto = False
                self.tool.reset_controls_state()
                return False
        
        def crack(self,ssid:str):
            '''
            破解wifi
            :ssid wifi名称
            '''
            try:
                self.iface.disconnect()  # 断开所有连接
                self.win.show_msg.send("正在断开现有连接...\n","black")
                time.sleep(1)
                if self.iface.status() in [const.IFACE_DISCONNECTED, const.IFACE_INACTIVE]:  # 测试是否已经断开网卡连接
                    self.win.show_msg.send("现有连接断开成功！\n\n","black")
                else:
                    self.win.show_msg.send("现有连接断开失败！\n\n","red")
                    return False
                self.win.show_msg.send(f"正在准备破解WiFi[{ssid}]...\n\n","black")

                if len(self.tool.pwd_dict_data) > 0:
                    pwd_dict_list = [ssids for ssids in self.tool.pwd_dict_data if ssids['ssid'] == ssid]
                    if len(pwd_dict_list) > 0:
                        self.win.show_msg.send(f"发现密码字典中存在相同SSID：{ssid}，开始尝试破解...\n\n","black")
                        for i,pwd_dict in enumerate(pwd_dict_list,1):
                            if self.tool.run==False:
                                self.win.show_msg.send("破解已终止.\n","black")
                                self.win.reset_controls_state.send()
                                return False
                            pwd = pwd_dict['pwd']
                            result = self.connect(ssid,pwd,'json',i)
                            if result and not self.is_auto:
                                self.win.show_info.send('破解成功',"连接成功，密码：%s\n(已复制到剪切板)"%(pwd))
                                return True
                            elif result:
                                return pwd
                        self.win.show_msg.send(f"已尝试完密码字典中[{ssid}]的所有密码，未成功破解\n\n","red")
                self.win.show_msg.send(f"开始尝试使用密码本破解WiFi[{ssid}]...\n\n","black")
                with open(self.tool.config_settings_data['pwd_txt_path'],'r', encoding='utf-8', errors='ignore') as lines:
                        for i,line in enumerate(lines,1):
                            if self.tool.run==False:
                                self.win.show_msg.send("破解已终止.\n","black")
                                self.win.reset_controls_state.send()
                                return False
                            pwd = line.strip()
                            result = self.connect(ssid,pwd,'txt',i)
                            if result and not self.is_auto:
                                self.win.show_info.send('破解成功',"连接成功，密码：%s\n(已复制到剪切板)"%(pwd))
                                return True
                            elif result:
                                return pwd
                        if not self.is_auto:
                            self.win.show_info.send('破解失败',"破解失败，已尝试完密码本中所有可能的密码")
                            self.tool.reset_controls_state()
                return False
            except Exception as r:
                self.win.show_error.send('错误警告','破解过程中发生未知错误 %s' %(r))
                self.win.show_msg.send(f"破解过程中发生未知错误 {r}\n\n","red")
                self.tool.reset_controls_state()
                return False
        
        def connect(self,ssid,pwd,filetype,count):
            '''
            连接wifi
            :ssid wifi名称
            :pwd wifi密码
            :filetype 密码本 txt / 密码字典 json
            :count 已尝试连接的次数
            '''
            try:
                self.iface.disconnect()  # * 断开所有连接
                # * 判断安全加密类型
                akm = self.ui.cbo_security_type.currentText()
                akm_i = self.ui.cbo_security_type.currentIndex()
                akm_v = 4
                akm_dict = _wifiutil_win.akm_str_to_value_dict
                if akm in akm_dict:
                    akm_v = akm_dict[akm]
                else:
                    akm_v = const.AKM_TYPE_NONE
                
                profile = Profile()  # * 创建wifi配置对象
                if akm_i == 0:
                    profile = self.profile_dict[ssid]
                else:
                    profile.ssid = ssid # * wifi名称
                    profile.auth = const.AUTH_ALG_OPEN  # * 网卡的开放
                    profile.akm = akm_v  # * wifi加密算法，一般是 WPA2PSK
                    profile.cipher = const.CIPHER_TYPE_CCMP # * 加密单元
                    
                profile.key = pwd   # * type: ignore #WiFi密码
                self.iface.remove_network_profile(profile)  # * 删除wifi文件
                tem_profile = self.iface.add_network_profile(profile)   # * 添加新的WiFi文件
                self.win.show_msg.send(f"正在进行第{count}次尝试...\n","black")
                self.iface.connect(tem_profile) # * 连接
                time.sleep(self.tool.config_settings_data['connect_time'])   # * 连接需要时间
                if self.iface.status() == const.IFACE_CONNECTED:    # * 判断是否连接成功
                    self.win.show_msg.send(f"连接成功，密码：{pwd}\n\n","green")
                    self.tool.reset_controls_state()
                    pyperclip.copy(pwd); # * 将密码复制到剪切板
                    if filetype != 'json':
                        self.tool.pwd_dict_data.append({'ssid':ssid,'pwd':pwd})
                        # * 直接将数据写入文件
                        with open(self.tool.pwd_dict_path, 'w',encoding='utf-8') as json_file:
                            json.dump(self.tool.pwd_dict_data, json_file, indent=4)
                    return True
                else:
                    self.win.show_msg.send(f"连接失败，密码是{pwd}\n\n","red")
                    self.iface.remove_network_profile(profile)  # * 删除wifi文件
                    return False

            except Exception as r:
                self.win.show_error.send('错误警告','连接wifi过程中发生未知错误 %s' %(r))
                self.win.show_msg.send(f"连接wifi过程中发生未知错误 {r}\n\n","red")
                self.tool.reset_controls_state()
                return False

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        
        system = platform.system()
        if system == 'Windows':
            print('当前系统是 Windows')
            import win32api,win32security,win32event # type: ignore
            #------------------- 互斥锁 -----------------------#
            MUTEX_NAME = "Global/wifi_crack_tool_mutex"
            def acquire_mutex():
                sa = win32security.SECURITY_ATTRIBUTES()
                sa.bInheritHandle = False  # 确保互斥量句柄不会被继承
                mutex = win32event.CreateMutex(sa, False, MUTEX_NAME)
                last_error = win32api.GetLastError()
                if last_error == 183:
                    return None
                elif last_error != 0:
                    raise ctypes.WinError(last_error)
                return mutex
            #==================================================#
            
            __mutex = None
            if PyWiFi().interfaces().__len__() <= 1:
                __mutex = acquire_mutex()
            
            window = MainWindow(__mutex)
            
        elif system == 'Linux':
            print('当前系统是 Linux')
            import fcntl
            #------------------- 互斥锁 -----------------------#
            LOCKFILE = "/tmp/wifi_crack_tool.lock"
            def acquire_lock():
                lock = os.open(LOCKFILE, os.O_RDWR | os.O_CREAT)
                try:
                    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB) # type: ignore
                    return lock
                except IOError:
                    return None

            def release_lock(lock):
                fcntl.flock(lock, fcntl.LOCK_UN) # type: ignore
                os.close(lock)
                os.remove(LOCKFILE)
            #==================================================#
                        
            __lock = None
            if PyWiFi().interfaces().__len__() <= 1:
                __lock = acquire_lock()
                
            window = MainWindow(__lock)
            
        elif system == 'Darwin':  # macOS
            print('当前系统是 macOS')
        else:
            print(f'当前系统是 {system}')
            
        window.show()
        app.exec()
        
        if window.tool.config_settings_data["pwd_txt_path"] == "":
            window.tool.config_settings_data["pwd_txt_path"] = "passwords.txt"
        with open(window.tool.config_file_path, 'w',encoding='utf-8') as config_file:
            json.dump(window.tool.config_settings_data, config_file, indent=4)
            
        sys.exit()
    finally:
        if '__mutex' in vars():
            if __mutex is not None:
                win32api.CloseHandle(__mutex)
        elif '__lock' in vars():
            if __lock is not None:
                release_lock(__lock)