# WiFi密码破解工具

## 免责声明
**本工具仅限于网络安全技术交流学习使用，请勿用于其他用途，若使用者有违反网络安全条例，与本人恕不相关。**

## 介绍

WiFiCrackTool是一款基于Python开发的拥有图形界面的WiFi密码破解工具

## 开发环境

Windows 10

Python 3.6.5

## 核心模块

pywifi

## 系统要求

Windows 10

非 Windows 10 系统请自行下载源码编译

## 编译方法

1. 下载 Python 3.6.5 并安装

2. 安装所需模块

   ```cmd
   pip install pywifi
   pip install pyinstaller
   ```

3. 编译 WifiCrackTool.py

   ```cmd
   pyinstaller -F -w WifiCrackTool.py
   ```

## 更新日志

### v1.0

- [修复]WiFi中文名称乱码，无法正常破解的问题。
- [新增]日志输出、破解成功后自动将密码复制到剪切板。
- [优化]部分功能
