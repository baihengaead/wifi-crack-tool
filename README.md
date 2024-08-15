# WiFi暴力破解工具

## 免责声明

**本项目所涉及的技术、思路和工具仅供学习交流，任何人不得将其用于非法用途和盈利，不得将其用于非授权渗透测试，否则后果自行承担，与本项目无关。使用本项目前请先阅读[法律法规](https://github.com/baihengaead/Awesome-Laws)。**

## 项目介绍

wifi_crack_tool是一款基于Python开发的拥有图形界面的WiFi密码暴力破解工具，使用本项目应遵循[MIT许可](https://github.com/baihengaead/wifi-crack-tool/blob/main/LICENSE)，可使用自定义密码本，且拥有自动保存破解成功后的WiFi SSID与密码到本地密码字典、在有多个无线网卡的情况下可以多开工具并行破解同一个或不同的WiFi。

支持 WPA、WPAPSK、WPA2、WPA2PSK 安全协议

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

Windows 10

Tips：理论支持Win10、Win11、Linux、MacOS（Linux 与 macOS 暂未测试，可自行尝试构建）

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
   pyinstaller -F -w WifiCrackTool.py
   ```

## 更新日志

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
