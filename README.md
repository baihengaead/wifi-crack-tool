# WiFi暴力破解工具

## 免责声明
**本项目所涉及的技术、思路和工具仅供学习交流，任何人不得将其用于非法用途和盈利，不得将其用于非授权渗透测试，否则后果自行承担，与本项目无关。使用本项目前请先阅读[法律法规](https://github.com/baihengaead/Awesome-Laws)。**

## 介绍

WiFiCrackTool是一款基于Python开发的拥有图形界面的WiFi密码暴力破解工具

## 开发环境

Windows 10

Python ≥3.6.5

## 核心模块

pywifi

## 系统要求

Windows 10

非 Windows 10 系统请自行下载源码编译

## 编译及打包方法

1. 下载 Python 3.6.5 并安装

2. 安装所需模块

   ```cmd
   pip install pywifi
   pip install pyinstaller
   ```
3. 编译 WifiCrackTool.py
   ```cmd
   python -u WifiCrackTool.py
   ```
4. 打包 WifiCrackTool.py

   ```cmd
   pyinstaller -F -w WifiCrackTool.py
   ```

## 更新日志

### v1.0

- [修复]WiFi中文名称乱码，无法正常破解的问题。
- [新增]日志输出、破解成功后自动将密码复制到剪切板。
- [优化]部分功能
