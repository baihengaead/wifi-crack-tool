# -*- coding: UTF-8 -*-
"""
macOS WiFi 工具模块
用于在 macOS 上进行 WiFi 扫描和连接操作
"""
import subprocess
import re
import time
from typing import Optional, List, Dict
from dataclasses import dataclass
from enum import IntEnum


class MacOSWiFiStatus(IntEnum):
    """WiFi 连接状态"""
    DISCONNECTED = 0
    SCANNING = 1
    CONNECTING = 2
    CONNECTED = 3
    INACTIVE = 4


@dataclass
class WiFiNetwork:
    """WiFi 网络信息，兼容 pywifi 的扫描结果"""
    ssid: str
    bssid: str
    rssi: int  # 信号强度 (dBm)
    channel: int
    security: str  # 安全类型
    # 以下属性用于兼容 pywifi
    auth: int = 0
    akm: list = None
    cipher: int = 0

    def __post_init__(self):
        if self.akm is None:
            # 根据 security 字符串推断 akm 类型
            if "WPA3" in self.security:
                self.akm = [6]  # WPA3SAE
            elif "WPA2" in self.security:
                self.akm = [4]  # WPA2PSK
            elif "WPA" in self.security:
                self.akm = [2]  # WPAPSK
            else:
                self.akm = [0]  # NONE


class MacOSWiFiInterface:
    """macOS WiFi 接口类，模拟 pywifi 的 Interface"""

    AIRPORT_PATH = "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport"

    def __init__(self, interface_name: str = "en0"):
        self.interface_name = interface_name
        self._status = MacOSWiFiStatus.DISCONNECTED
        self._scan_results: List[WiFiNetwork] = []

    def name(self) -> str:
        """返回接口名称"""
        return self.interface_name

    def status(self) -> int:
        """获取当前连接状态"""
        try:
            result = subprocess.run(
                ["networksetup", "-getairportnetwork", self.interface_name],
                capture_output=True, text=True, timeout=10
            )
            output = result.stdout + result.stderr
            if "You are not associated" in output or "is not associated" in output:
                return MacOSWiFiStatus.DISCONNECTED
            elif "Current Wi-Fi Network" in output:
                return MacOSWiFiStatus.CONNECTED
            # 检查输出中是否包含网络名称（说明已连接）
            if result.returncode == 0 and result.stdout.strip() and "Wi-Fi" not in result.stdout:
                return MacOSWiFiStatus.CONNECTED
            return MacOSWiFiStatus.INACTIVE
        except Exception:
            return MacOSWiFiStatus.INACTIVE

    def scan(self) -> None:
        """开始扫描 WiFi"""
        self._status = MacOSWiFiStatus.SCANNING

    def scan_results(self) -> List[WiFiNetwork]:
        """获取扫描结果"""
        networks = []
        try:
            # 使用 system_profiler 获取 WiFi 信息（airport 已废弃）
            result = subprocess.run(
                ["system_profiler", "SPAirPortDataType"],
                capture_output=True, text=True, timeout=30
            )

            if result.returncode != 0:
                print(f"扫描失败: {result.stderr}")
                return networks

            lines = result.stdout.split('\n')
            current_network = None
            in_other_networks = False
            in_current_network = False
            network_data = {}

            for line in lines:
                stripped = line.strip()

                # 检测当前连接的网络部分
                if "Current Network Information:" in line:
                    in_current_network = True
                    in_other_networks = False
                    continue

                # 检测其他网络部分
                if "Other Local Wi-Fi Networks:" in line:
                    in_other_networks = True
                    in_current_network = False
                    continue

                # 解析网络信息
                if (in_other_networks or in_current_network) and stripped:
                    # 网络名称行（以冒号结尾，不包含其他信息）
                    if stripped.endswith(':') and not any(key in stripped for key in ['PHY Mode:', 'Channel:', 'Security:', 'Signal']):
                        # 保存之前的网络
                        if network_data and 'ssid' in network_data:
                            network = WiFiNetwork(
                                ssid=network_data.get('ssid', ''),
                                bssid=network_data.get('bssid', ''),
                                rssi=network_data.get('rssi', -100),
                                channel=network_data.get('channel', 0),
                                security=network_data.get('security', 'Unknown')
                            )
                            networks.append(network)

                        # 开始新网络
                        network_data = {'ssid': stripped[:-1]}  # 去掉末尾冒号
                    elif 'Security:' in stripped:
                        network_data['security'] = stripped.split(':')[-1].strip()
                    elif 'Signal / Noise:' in stripped:
                        try:
                            signal_part = stripped.split(':')[-1].strip()
                            rssi_str = signal_part.split('/')[0].strip().replace('dBm', '').strip()
                            network_data['rssi'] = int(rssi_str)
                        except (ValueError, IndexError):
                            network_data['rssi'] = -100
                    elif 'Channel:' in stripped:
                        try:
                            channel_part = stripped.split(':')[-1].strip()
                            channel_str = channel_part.split()[0]
                            network_data['channel'] = int(channel_str)
                        except (ValueError, IndexError):
                            network_data['channel'] = 0

                # 结束解析（遇到空行或新的主要部分）
                if not stripped and (in_other_networks or in_current_network):
                    if network_data and 'ssid' in network_data:
                        # 如果没有安全信息，可能已经到了下一个网络或部分结束
                        pass

            # 保存最后一个网络
            if network_data and 'ssid' in network_data:
                network = WiFiNetwork(
                    ssid=network_data.get('ssid', ''),
                    bssid=network_data.get('bssid', ''),
                    rssi=network_data.get('rssi', -100),
                    channel=network_data.get('channel', 0),
                    security=network_data.get('security', 'Unknown')
                )
                networks.append(network)

            self._scan_results = networks
            self._status = MacOSWiFiStatus.DISCONNECTED

        except subprocess.TimeoutExpired:
            print("扫描超时")
        except Exception as e:
            print(f"扫描错误: {e}")

        return networks

    def disconnect(self) -> bool:
        """断开当前 WiFi 连接"""
        try:
            result = subprocess.run(
                ["networksetup", "-setairportpower", self.interface_name, "off"],
                capture_output=True, text=True, timeout=10
            )
            time.sleep(1)
            result = subprocess.run(
                ["networksetup", "-setairportpower", self.interface_name, "on"],
                capture_output=True, text=True, timeout=10
            )
            return result.returncode == 0
        except Exception as e:
            print(f"断开连接失败: {e}")
            return False

    def connect(self, ssid: str, password: str, security: str = "WPA2") -> bool:
        """
        连接到指定的 WiFi 网络

        Args:
            ssid: WiFi 名称
            password: WiFi 密码
            security: 安全类型 (WPA, WPA2, WPA3 等)

        Returns:
            是否连接成功
        """
        try:
            self._status = MacOSWiFiStatus.CONNECTING

            # 使用 networksetup 连接 WiFi
            result = subprocess.run(
                ["networksetup", "-setairportnetwork", self.interface_name, ssid, password],
                capture_output=True, text=True, timeout=30
            )

            # 检查连接结果
            if result.returncode == 0 and "Error" not in result.stderr:
                # 验证连接状态
                time.sleep(2)
                if self.status() == MacOSWiFiStatus.CONNECTED:
                    self._status = MacOSWiFiStatus.CONNECTED
                    return True

            self._status = MacOSWiFiStatus.DISCONNECTED
            return False

        except subprocess.TimeoutExpired:
            print("连接超时")
            self._status = MacOSWiFiStatus.DISCONNECTED
            return False
        except Exception as e:
            print(f"连接错误: {e}")
            self._status = MacOSWiFiStatus.DISCONNECTED
            return False

    def get_current_network(self) -> Optional[str]:
        """获取当前连接的 WiFi 名称"""
        try:
            result = subprocess.run(
                ["networksetup", "-getairportnetwork", self.interface_name],
                capture_output=True, text=True, timeout=10
            )
            if "Current Wi-Fi Network:" in result.stdout:
                return result.stdout.split(":")[-1].strip()
            return None
        except Exception:
            return None

    def remove_network_profile(self, profile) -> None:
        """
        移除网络配置（pywifi 兼容方法）
        在 macOS 上这是一个空操作，因为我们直接通过 networksetup 连接
        """
        pass

    def add_network_profile(self, profile) -> 'MacOSProfile':
        """
        添加网络配置（pywifi 兼容方法）
        在 macOS 上返回相同的 profile，实际连接在 connect 中处理
        """
        return profile

    def connect_with_profile(self, profile) -> bool:
        """
        使用 profile 对象连接 WiFi（pywifi 兼容方法）

        Args:
            profile: MacOSProfile 对象，包含 ssid 和 key

        Returns:
            是否连接成功
        """
        return self.connect(profile.ssid, profile.key)


class MacOSWiFi:
    """macOS WiFi 管理类，模拟 pywifi 的 PyWiFi"""

    def __init__(self):
        self._interfaces: List[MacOSWiFiInterface] = []
        self._detect_interfaces()

    def _detect_interfaces(self) -> None:
        """检测可用的 WiFi 接口"""
        try:
            # 获取所有网络接口
            result = subprocess.run(
                ["networksetup", "-listallhardwareports"],
                capture_output=True, text=True, timeout=10
            )

            lines = result.stdout.split('\n')
            i = 0
            while i < len(lines):
                if "Wi-Fi" in lines[i] or "AirPort" in lines[i]:
                    # 下一行包含设备名称
                    if i + 1 < len(lines) and "Device:" in lines[i + 1]:
                        device = lines[i + 1].split(":")[-1].strip()
                        self._interfaces.append(MacOSWiFiInterface(device))
                i += 1

            # 如果没有找到，默认使用 en0
            if not self._interfaces:
                self._interfaces.append(MacOSWiFiInterface("en0"))

        except Exception as e:
            print(f"检测网络接口失败: {e}")
            self._interfaces.append(MacOSWiFiInterface("en0"))

    def interfaces(self) -> List[MacOSWiFiInterface]:
        """返回所有 WiFi 接口"""
        return self._interfaces


# 状态常量，与 pywifi.const 兼容
class MacOSConst:
    IFACE_DISCONNECTED = MacOSWiFiStatus.DISCONNECTED
    IFACE_SCANNING = MacOSWiFiStatus.SCANNING
    IFACE_CONNECTING = MacOSWiFiStatus.CONNECTING
    IFACE_CONNECTED = MacOSWiFiStatus.CONNECTED
    IFACE_INACTIVE = MacOSWiFiStatus.INACTIVE

    # 安全类型
    AKM_TYPE_NONE = 0
    AKM_TYPE_WPA = 1
    AKM_TYPE_WPAPSK = 2
    AKM_TYPE_WPA2 = 3
    AKM_TYPE_WPA2PSK = 4
    AKM_TYPE_WPA3 = 5
    AKM_TYPE_WPA3SAE = 6

    AUTH_ALG_OPEN = 0
    CIPHER_TYPE_CCMP = 0


# 兼容 pywifi 的 Profile 类
class MacOSProfile:
    def __init__(self):
        self.ssid = ""
        self.auth = MacOSConst.AUTH_ALG_OPEN
        self.akm = [MacOSConst.AKM_TYPE_WPA2PSK]
        self.cipher = MacOSConst.CIPHER_TYPE_CCMP
        self.key = ""


if __name__ == "__main__":
    # 测试代码
    print("=== macOS WiFi 工具测试 ===")

    wifi = MacOSWiFi()
    interfaces = wifi.interfaces()

    print(f"\n找到 {len(interfaces)} 个 WiFi 接口:")
    for iface in interfaces:
        print(f"  - {iface.name()}")
        print(f"    状态: {iface.status()}")
        current = iface.get_current_network()
        if current:
            print(f"    当前连接: {current}")

    if interfaces:
        print("\n正在扫描 WiFi...")
        iface = interfaces[0]
        iface.scan()
        time.sleep(3)
        results = iface.scan_results()

        print(f"\n找到 {len(results)} 个 WiFi 网络:")
        for network in results[:10]:  # 只显示前10个
            print(f"  - {network.ssid}")
            print(f"    信号: {network.rssi} dBm, 频道: {network.channel}, 安全: {network.security}")
