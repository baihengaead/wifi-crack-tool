# WiFi暴力破解工具

## 免责声明

**本项目所涉及的技术、思路和工具仅供学习交流，任何人不得将其用于非法用途和盈利，不得将其用于非授权渗透测试，否则后果自行承担，与本项目无关。使用本项目前请先阅读[法律法规](https://github.com/baihengaead/Awesome-Laws)。**

## 项目介绍

wifi_crack_tool是一款基于Python开发的拥有图形界面的WiFi密码暴力破解工具，支持多平台，使用本项目应遵循[MIT许可](https://github.com/baihengaead/wifi-crack-tool/blob/main/LICENSE)，可使用自定义密码本，且拥有自动保存破解成功后的WiFi SSID与密码到本地密码字典、在有多个无线网卡的情况下可以多开工具并行破解同一个或不同的WiFi。

支持 WPA、WPAPSK、WPA2、WPA2PSK、WPA3、WPA3SAE 安全协议

## 如何使用

#### 简单使用

##### 使用

首先测试你的无线网卡在 扫描wifi 和 连接wifi 时最佳的延时时长（以能成功扫描和成功连接为准），然后设置 扫描时间 和 连接时间。

接下来正常使用就可以啦。

##### 结果

破解的结果会在日志中显示，破解完成后会弹窗提示，并自动将破解得到的密码复制到剪切板。

#### 自动运行

##### 介绍

自动破解扫描到的所有WiFi

##### 使用

1. 选择你要使用的无线网卡
2. 扫描WiFi
3. WiFi名称选择 ——全部——
4. 开始破解

##### 结果

破解的结果会在日志中显示，全部破解完成后会弹窗提示。

结果示例：

```txt
(1)   wifi名称1   密码1
(2)   wifi名称2   密码2
...
```

#### 多开并发

##### 要求

电脑至少有2个无线网卡，且都可以正常使用

##### 使用

以有2个无线网卡为例

1. 打开2次 `wifi_crack_tool.exe`或者 `python wifi_crack_tool.py`
2. 选择不同的无线网卡
3. 扫描WiFi
4. 选择需要破解的WiFi
5. 开始破解

##### 结果

见 简单使用 / 自动运行

#### 密码本

##### 默认文件路径

```cmd
./passwords.txt
```

##### 文件格式

```txt
password1
password2
password3
...
```

#### 密码字典

##### 文件路径

```cmd
./dict/pwdict.json
```

##### 文件格式

```json
[
    {
        "ssid":"wifi_1",
        "pwd":"password1"
    },
    {
        "ssid":"wifi_2",
        "pwd":"password2"
    },
    {
        "ssid":"wifi_3",
        "pwd":"password3"
    },
]
```

#### 日志

##### 文件路径

```cmd
./log/wifi_crack_log_{datetime}.txt
```

## 开发环境

Python ≥ 3.11.x（推荐：3.11.9）

## 核心模块

pywifi、pyside6

## 系统要求

- Windows 10 及以上 
- Ubuntu 22.04 及以上版本 **（实验性）**
- 其它支持 Python 3.11.x 以上的Linux系统 **（实验性）**

Tips：支持Win10、Win11、Linux，MacOS暂不支持

## 如何修改GUI

1. [下载 Python 3.11.9](https://www.python.org/downloads/release/python-3119/) 并安装
2. 安装所需模块

   ```cmd
   pip install -r requirements.txt
   ```
3. 启动QT Designer pyside6-designer

   ```cmd
   pyside6-designer
   ```
4. 在QT Designer中打开wifi_crack_tool_gui.ui
5. 使用设计器对UI进行调整

## 如何运行以及打包

### Windows

1. [下载 Python 3.11.9](https://www.python.org/downloads/release/python-3119/) 并安装

2. 安装所需模块

   ```cmd
   pip install -r requirements.txt
   ```

3. 编译 wifi_crack_tool_gui.ui

   ```cmd
   pyside6-uic wifi_crack_tool_gui.ui -o wifi_crack_tool_gui.py
   ```

4. 编译运行 wifi_crack_tool.py

   ```cmd
   python -u wifi_crack_tool.py
   ```

5. 打包 wifi_crack_tool.py

   ```cmd
   pyinstaller -F -w wifi_crack_tool.py
   ```

### Linux（以 Ubuntu 24.04 为例）

1. 更新软件包

   ```shell
   sudo apt update
   sudo apt upgrade
   ```

2. 安装QT GUI依赖库 以及 剪切板依赖库

   ```shell
   sudo apt install libxcb-cursor0
   sudo apt install xclip
   ```

3. 安装python3虚拟环境库

   ```shell
   sudo apt install python3-venv
   ```

4. 创建python3虚拟环境

   ```shell
   python3 -m venv wifi-crack-tool-venv
   ```

5. 激活python3虚拟环境

   ```shell
   source wifi-crack-tool-venv/bin/activate
   ```

6. 安装所需模块（Linux需要将 requirements.txt 中的 `pywin32>=306` 删除）

   ```shell
   pip3 install -r requirements.txt
   ```

7. 编译 wifi_crack_tool_gui.ui

   ```shell
   pyside6-uic wifi_crack_tool_gui.ui -o wifi_crack_tool_gui.py
   ```

8. 编译运行 wifi_crack_tool.py

   ```shell
   python3 -u wifi_crack_tool.py
   ```

9. 打包 wifi_crack_tool.py

   ```shell
   pyinstaller -F -w wifi_crack_tool.py
   ```

## 更新日志

### v1.2.5

- **[新增]** 支持在破解过程中**暂停**。([#26](https://github.com/baihengaead/wifi-crack-tool/issues/26))
- **[修复]** 在设备的**WLAN功能关闭**时，**扫描WiFi会抛出意外错误**的问题。([#28](https://github.com/baihengaead/wifi-crack-tool/issues/28))
- **[修复]** 在自动破解全部WiFi的情况下，连接完成一个WiFi后，所有**按钮的状态会被重置**的问题。

### v1.2.4

- **[新增]** 对**WPA3**的支持（Linux）。

### v1.2.3

- **[新增]** 对**WPA3**的支持（Windows）。
- **[新增]** **自动获取**安全类型的功能（Windows）。
- **[优化]** SSID的utf-8**编码转换**（Windows）。

### v1.2.2

- **[修复]** 在多网卡的情况下**意外的提示**了 “应用程序的另一个实例已经在运行。” 的问题。([#13](https://github.com/baihengaead/wifi-crack-tool/issues/13))
- **[修复]** 在部分情况下，进行utf-8**编码转换**时，出现转换**异常**的问题。([#13](https://github.com/baihengaead/wifi-crack-tool/issues/13))
- **[修复]** 在破解中文WiFi后，连接的**中文WiFi名称乱码**的问题。

### v1.2.1

- **[优化]** 对Linux平台支持。

### v1.2.0

- **[新增]** 对扫描到的所有WiFi进行**自动破解**。([#10](https://github.com/baihengaead/wifi-crack-tool/issues/10))

### v1.1.1

- **[修复]** 部分已知问题。

### v1.1.0

- **[重构]** GUI框架从**tkinter**更换为了**pyside6**，对UI进行了调整。
- **[新增]** 在UI可以设置**扫描时间**、**连接时间**以及选择**无线网卡**的功能。
- **[新增]** 打开**读取配置**文件，关闭**保存配置**文件的功能。
- **[新增]** 破解成功将**SSID与密码保存在本地密码字典**中，并在破解WiFi时优先从本地密码字典检索相关密码进行破解。
- **[新增]** 在拥**有多个无线网卡**的情况下，可以**多开工具**并选择不同网卡**并行破解**。
- **[修复]** 在搜索不到WiFi时报错的问题。
- **[优化]** 消息框中出现**破解成功**、**破解失败**以及**异常报错**的消息时，**单独**以不同颜色**高亮显示**。
- **[优化]** 部分功能。

### v1.0.0

- **[新增]** 日志输出、破解成功后**自动将密码复制到剪切板**。
- **[修复]** WiFi**中文名称乱码**，**无法正常破解**的问题。
- **[优化]** 部分功能。
