import platform
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import uuid
import socket
import requests
import urllib.parse
import json
import subprocess
import threading
import time
import webbrowser
import math
import concurrent.futures
import os
import websocket

class NetFucker:
    def __init__(self):
        self.root = tk.Tk()
        self.current_version = "v20250306_01"  # 定义为GitHub Release版本号
        self.release = True  # 控制是否进行GitHub Actions构建和发布
        self.root.title(f"SHBS NetFucker {self.current_version}")
        self.root.geometry("600x700")
        self.root.configure(bg='#f0f0f0')
        
        # 获取操作系统信息
        self.os_type = platform.system()
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)
        
        # 初始化WebSocket连接
        self.ws = None
        self.ws_connected = False
        self.ws_reconnect_timer = None
        self.online_users = []
        self.total_network_upload = 0
        self.total_network_download = 0
        
        # 系统信息显示
        info_frame = ttk.LabelFrame(self.main_frame, text="系统信息", padding="5")
        info_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(info_frame, text="操作系统:").grid(row=0, column=0, sticky=tk.W)
        self.os_label = ttk.Label(info_frame, text=f"{self.os_type}")
        self.os_label.grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(info_frame, text="MAC地址:").grid(row=1, column=0, sticky=tk.W)
        self.mac_label = ttk.Label(info_frame, text="获取中...")
        self.mac_label.grid(row=1, column=1, sticky=tk.W)
        
        ttk.Label(info_frame, text="IP地址:").grid(row=2, column=0, sticky=tk.W)
        self.ip_label = ttk.Label(info_frame, text="获取中...")
        self.ip_label.grid(row=2, column=1, sticky=tk.W)
        
        # 网络状态和流量监控
        monitor_frame = ttk.LabelFrame(self.main_frame, text="网络监控", padding="5")
        monitor_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(monitor_frame, text="网络状态:").grid(row=0, column=0, sticky=tk.W)
        self.status_label = ttk.Label(monitor_frame, text="未登录", foreground="#666666")
        self.status_label.grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(monitor_frame, text="上传速度:").grid(row=1, column=0, sticky=tk.W)
        self.upload_label = ttk.Label(monitor_frame, text="0 KB/s", foreground="#666666")
        self.upload_label.grid(row=1, column=1, sticky=tk.W)
        
        ttk.Label(monitor_frame, text="下载速度:").grid(row=2, column=0, sticky=tk.W)
        self.download_label = ttk.Label(monitor_frame, text="0 KB/s", foreground="#666666")
        self.download_label.grid(row=2, column=1, sticky=tk.W)
        
        # 添加总流量显示
        ttk.Label(monitor_frame, text="总上传流量:").grid(row=3, column=0, sticky=tk.W)
        self.total_upload_label = ttk.Label(monitor_frame, text="0 B", foreground="#666666")
        self.total_upload_label.grid(row=3, column=1, sticky=tk.W)
        
        ttk.Label(monitor_frame, text="总下载流量:").grid(row=4, column=0, sticky=tk.W)
        self.total_download_label = ttk.Label(monitor_frame, text="0 B", foreground="#666666")
        self.total_download_label.grid(row=4, column=1, sticky=tk.W)
        
        # 添加在线用户统计
        stats_frame = ttk.LabelFrame(self.main_frame, text="在线用户统计", padding="5")
        stats_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(stats_frame, text="在线用户数:").grid(row=0, column=0, sticky=tk.W)
        self.online_count_label = ttk.Label(stats_frame, text="0", foreground="#666666")
        self.online_count_label.grid(row=0, column=1, sticky=tk.W)
        
        # 操作按钮区域
        operation_frame = ttk.LabelFrame(self.main_frame, text="操作", padding="10")
        operation_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # 网络连接按钮
        network_frame = ttk.Frame(operation_frame)
        network_frame.pack(fill=tk.X, pady=5)
        
        self.connect_button = ttk.Button(network_frame, text="连接网络", command=self.connect_wifi, style="Action.TButton")
        self.connect_button.pack(side=tk.LEFT, padx=5, expand=True)
        
        self.login_button = ttk.Button(network_frame, text="登录", command=self.login, style="Action.TButton")
        self.login_button.pack(side=tk.LEFT, padx=5, expand=True)
        
        # 版本控制区域
        version_frame = ttk.LabelFrame(self.main_frame, text="版本信息", padding="10")
        version_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        version_info_frame = ttk.Frame(version_frame)
        version_info_frame.pack(fill=tk.X, pady=5)
        
        self.version_label = ttk.Label(version_info_frame, text=f"当前版本: {self.current_version}", foreground="#666666")
        self.version_label.pack(side=tk.LEFT, padx=5)
        
        self.latest_version_label = ttk.Label(version_info_frame, text="最新版本: 检查中...", foreground="#666666")
        self.latest_version_label.pack(side=tk.LEFT, padx=5)
        
        update_button_frame = ttk.Frame(version_frame)
        update_button_frame.pack(fill=tk.X, pady=5)
        
        self.check_update_button = ttk.Button(update_button_frame, text="检查更新", command=self.check_update, style="Action.TButton")
        self.check_update_button.pack(expand=True, padx=5)
        
    
        
        # 日志显示区域
        log_frame = ttk.LabelFrame(self.main_frame, text="运行日志", padding="5")
        log_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=20, width=60)
        self.log_text.pack(expand=True, fill='both')
        self.log_text.configure(font=('Courier', 10))
        
        # 配置日志区域的网格权重
        self.main_frame.grid_rowconfigure(5, weight=1)
        
        # 初始检查更新
        threading.Thread(target=self.check_update, daemon=True).start()
        
        # 初始化系统信息
        self.init_system_info()
        
        # 在界面显示后执行网络检测
        self.root.after(1000, lambda: threading.Thread(target=lambda: self.check_network_status(3), daemon=True).start())
        
        # 启动流量监控
        self.start_traffic_monitor()
        
        # 启动WebSocket连接
        self.connect_websocket()
    
    def connect_websocket(self):
        def ws_connect():
            try:
                import websocket
                self.ws = websocket.WebSocketApp(
                    "wss://api.shbs.club",
                    on_message=self.on_ws_message,
                    on_error=self.on_ws_error,
                    on_close=self.on_ws_close,
                    on_open=self.on_ws_open
                )
                self.ws.run_forever()
            except Exception as e:
                self.log(f"WebSocket连接错误: {str(e)}")
                if not self.ws_reconnect_timer:
                    self.ws_reconnect_timer = self.root.after(5000, self.connect_websocket)
        
        threading.Thread(target=ws_connect, daemon=True).start()
    
    def on_ws_open(self, ws):
        self.ws_connected = True
        self.log("已连接到统计服务器")
        # 发送初始化数据
        self.send_ws_message({
            'type': 'init',
            'mac_address': self.mac_label.cget("text"),
            'ip_address': self.ip_label.cget("text")
        })
    
    def on_ws_message(self, ws, message):
        try:
            data = json.loads(message)
            self.online_users = data.get('users', [])
            self.total_network_upload = data.get('total_upload', 0)
            self.total_network_download = data.get('total_download', 0)
            
            # 更新界面显示
            self.root.after(0, lambda: self.update_stats_display(data))
        except Exception as e:
            self.log(f"处理WebSocket消息错误: {str(e)}")
    
    def on_ws_error(self, ws, error):
        self.log(f"WebSocket错误: {str(error)}")
    
    def on_ws_close(self, ws, close_status_code, close_msg):
        self.ws_connected = False
        self.log("与统计服务器的连接已断开")
        if not self.ws_reconnect_timer:
            self.ws_reconnect_timer = self.root.after(5000, self.connect_websocket)
    
    def send_ws_message(self, data):
        if self.ws and self.ws_connected:
            try:
                self.ws.send(json.dumps(data))
            except Exception as e:
                self.log(f"发送WebSocket消息错误: {str(e)}")
    
    def update_stats_display(self, data):
        # 更新在线用户数
        self.online_count_label.config(text=str(data.get('online_count', 0)))
    
    def log(self, message):
        self.log_text.insert(tk.END, f"{time.strftime('%Y-%m-%d %H:%M:%S')} {message}\n")
        self.log_text.see(tk.END)
    
    def check_network_status(self, times=1):
        success_count = 0
        total_latency = 0
        test_url = "http://www.baidu.com"
        
        for i in range(times):
            try:
                start_time = time.time()
                response = requests.get(test_url, timeout=2)
                end_time = time.time()
                latency = (end_time - start_time) * 1000  # 转换为毫秒
                
                if response.status_code == 200:
                    success_count += 1
                    total_latency += latency
                    self.log(f"网络检测 #{i+1}: 成功 - 延迟: {latency:.2f}ms")
                else:
                    self.log(f"网络检测 #{i+1}: 失败 - HTTP状态码: {response.status_code}")
                time.sleep(1)  # 每次检测间隔1秒
            except Exception as e:
                self.log(f"网络检测 #{i+1}: 错误 - {str(e)}")
        
        # 根据成功次数判断网络状态
        if success_count >= times/2:
            avg_latency = total_latency / success_count if success_count > 0 else 0
            status_text = f"已连接到因特网 (平均延迟: {avg_latency:.2f}ms)"
            self.status_label.config(text=status_text, foreground="#28a745")
            return True
        else:
            self.status_label.config(text="未连接", foreground="#dc3545")
            return False
    
    def init_system_info(self, max_retries=3, retry_interval=1):
        # 获取MAC地址
        mac_success = False
        for retry in range(max_retries):
            try:
                if self.os_type == "Windows":
                    try:
                        result = subprocess.run(['getmac', '/fo', 'csv', '/nh'], 
                                              capture_output=True, 
                                              text=True)
                        if result.returncode == 0:
                            mac = result.stdout.split(',')[0].strip('"')
                            self.mac_label.config(text=mac.upper())
                            mac_success = True
                            break
                        else:
                            raise Exception("获取MAC地址失败")
                    except:
                        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
                                        for elements in range(0,8*6,8)][::-1])
                        self.mac_label.config(text=mac.upper())
                        mac_success = True
                        break
                else:
                    mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
                                    for elements in range(0,8*6,8)][::-1])
                    self.mac_label.config(text=mac.upper())
                    mac_success = True
                    break
            except Exception as e:
                if retry < max_retries - 1:
                    self.log(f"获取MAC地址失败 (尝试 {retry + 1}/{max_retries}): {str(e)}")
                    time.sleep(retry_interval)
                else:
                    self.mac_label.config(text="无法获取MAC地址")
                    self.log(f"获取MAC地址失败，已达到最大重试次数: {str(e)}")
        
        # 获取IP地址
        ip_success = False
        for retry in range(max_retries):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                ip = s.getsockname()[0]
                s.close()
                self.ip_label.config(text=ip)
                self.log(f"获取IP地址: {ip}")
                ip_success = True
                break
            except Exception as e:
                if retry < max_retries - 1:
                    self.log(f"获取IP地址失败 (尝试 {retry + 1}/{max_retries}): {str(e)}")
                    time.sleep(retry_interval)
                else:
                    self.ip_label.config(text="无法获取IP地址")
                    self.log(f"获取IP地址失败，已达到最大重试次数: {str(e)}")
        
        return mac_success and ip_success
    
    def login(self):
        try:
            # 禁用登录按钮，防止重复点击
            self.login_button.config(state='disabled')
            self.status_label.config(text="登录中...", foreground="#666666")
            
            mac = self.mac_label.cget("text").replace(":", "-")
            ip = self.ip_label.cget("text")
            
            # 设置请求超时
            timeout = 10
            
            try:
                # 初始化请求
                init_url = f"http://172.16.1.4:8080/portal/?wlanusermac={mac}&wlanuserip={ip}&wlanacname=AC&ssid=wlan-teacher"
                self.log(f"发送初始化请求: {init_url}")
                response = requests.get(init_url, timeout=timeout)
                self.log(f"初始化响应状态码: {response.status_code}")
                
                # 检查初始化响应
                if response.status_code != 200:
                    raise Exception(f"初始化请求失败: HTTP {response.status_code}")
                
                # 登录请求
                login_data = {
                    'userName': 'tempstu',
                    'userPwd': 'c2hiczIwMjU=',  # Base64编码的密码
                    'userip': ip,
                    'usermac': 'null',
                    'wlanssid': 'wlan-teacher',
                    'language': 'English',
                    'portalProxyIP': '172.16.1.4',
                    'portalProxyPort': '50200',
                    'dcPwdNeedEncrypt': '1',
                    'assignIpType': '0',
                    'appRootUrl': 'http://172.16.1.4:8080/portal/'
                }
                
                login_url = 'http://172.16.1.4:8080/portal/pws?t=li'
                headers = {
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'X-Requested-With': 'XMLHttpRequest'
                }
                
                self.log(f"发送登录请求: {login_url}")
                self.log(f"登录数据: {json.dumps(login_data, ensure_ascii=False)}")
                
                response = requests.post(login_url, data=login_data, headers=headers, timeout=timeout)
                
                self.log(f"登录响应状态码: {response.status_code}")
                
                # 尝试解析响应内容
                try:
                    response_data = response.json()
                    self.log(f"登录响应内容: {json.dumps(response_data, ensure_ascii=False, indent=2)}")
                    
                    # 检查响应中的错误信息
                    if 'errorMsg' in response_data:
                        raise Exception(f"登录失败: {response_data['errorMsg']}")
                except ValueError:
                    self.log(f"登录响应内容: {response.text}")
                
                if response.status_code == 200:
                    self.status_label.config(text="登录成功", foreground="#28a745")
                    self.log("登录成功")
                    self.log("==================================")
                    self.log("Thank you for using Milk NetFucker.")
                    self.log("Official Website: net.shbs.club")
                    self.log("==================================")
                    # 登录成功后检测网络状态和更新
                    threading.Thread(target=lambda: self.check_network_status(3), daemon=True).start()
                    threading.Thread(target=self.check_update, daemon=True).start()
                else:
                    raise Exception(f"登录失败: HTTP {response.status_code}")
                    
            except requests.Timeout:
                raise Exception("请求超时，请检查网络连接")
            except requests.ConnectionError:
                raise Exception("无法连接到服务器，请检查网络连接")
            except json.JSONDecodeError:
                raise Exception("服务器返回的数据格式错误")
                
        except Exception as e:
            error_msg = str(e)
            self.status_label.config(text=f"登录错误", foreground="#dc3545")
            self.log(f"登录错误: {error_msg}")
            
        finally:
            # 恢复登录按钮状态
            self.login_button.config(state='normal')

    
    def connect_wifi(self):
        try:
            # 禁用连接按钮，防止重复点击
            self.connect_button.config(state='disabled')
            self.status_label.config(text="连接中...", foreground="#666666")
            self.log("正在尝试连接wlan-teacher网络...")
            
            if self.os_type == "Windows":
                # Windows系统使用netsh命令连接WiFi
                result = subprocess.run(
                    ['netsh', 'wlan', 'connect', 'name=wlan-teacher'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
            else:
                # macOS系统使用networksetup命令连接WiFi
                result = subprocess.run(
                    ['networksetup', '-setairportnetwork', 'en0', 'wlan-teacher'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
            
            if result.returncode == 0:
                self.log("成功连接到wlan-teacher网络")
                self.status_label.config(text="已连接到wlan-teacher", foreground="#28a745")
                # 连接成功后更新IP地址
                self.init_system_info()
                # 检查网络状态
                threading.Thread(target=lambda: self.check_network_status(3), daemon=True).start()
            else:
                error_msg = result.stderr.strip() or "连接失败"
                self.log(f"连接错误: {error_msg}")
                self.status_label.config(text="连接失败", foreground="#dc3545")
                
        except Exception as e:
            self.log(f"连接错误: {str(e)}")
            self.status_label.config(text="连接错误", foreground="#dc3545")
            
        finally:
            # 恢复连接按钮状态
            self.connect_button.config(state='normal')

    def start_traffic_monitor(self):
        # 初始化流量统计变量
        self.total_upload = 0
        self.total_download = 0
        self.last_report_time = time.time()
        
        # 启动流量监控线程
        threading.Thread(target=self.monitor_traffic, daemon=True).start()

    def monitor_traffic(self):
        while True:
            try:
                # 获取当前网络接口的流量数据
                if self.os_type == "Windows":
                    # Windows系统使用wmic命令获取网络流量
                    upload_cmd = subprocess.run(['wmic', 'path', 'Win32_PerfFormattedData_Tcpip_NetworkInterface', 'get', 'BytesSentPersec'], capture_output=True, text=True)
                    download_cmd = subprocess.run(['wmic', 'path', 'Win32_PerfFormattedData_Tcpip_NetworkInterface', 'get', 'BytesReceivedPersec'], capture_output=True, text=True)
                    
                    # 解析命令输出
                    current_upload = sum(int(line.strip()) for line in upload_cmd.stdout.split('\n')[1:] if line.strip().isdigit())
                    current_download = sum(int(line.strip()) for line in download_cmd.stdout.split('\n')[1:] if line.strip().isdigit())
                else:
                    # macOS系统使用netstat命令获取网络流量
                    cmd = subprocess.run(['netstat', '-I', 'en0'], capture_output=True, text=True)
                    lines = cmd.stdout.split('\n')
                    if len(lines) >= 2:
                        stats = lines[1].split()
                        if len(stats) >= 7:
                            current_upload = int(stats[7])
                            current_download = int(stats[6])
                        else:
                            current_upload = current_download = 0
                    else:
                        current_upload = current_download = 0
                
                # 计算速度（字节/秒）
                current_time = time.time()
                time_diff = current_time - self.last_report_time
                
                if time_diff > 0:
                    upload_speed = (current_upload - self.total_upload) / time_diff
                    download_speed = (current_download - self.total_download) / time_diff
                    
                    # 更新总流量
                    self.total_upload = current_upload
                    self.total_download = current_download
                    self.last_report_time = current_time
                    
                    # 更新界面显示
                    self.root.after(0, lambda: self.update_traffic_display(upload_speed, download_speed))
                    
                    # 发送流量数据到WebSocket服务器
                    self.send_ws_message({
                        'type': 'traffic_update',
                        'mac_address': self.mac_label.cget("text"),
                        'upload_speed': upload_speed,
                        'download_speed': download_speed,
                        'total_upload': self.total_upload,
                        'total_download': self.total_download
                    })
                
            except Exception as e:
                self.log(f"流量监控错误: {str(e)}")
            
            # 每秒更新一次
            time.sleep(1)
    
    def update_traffic_display(self, upload_speed, download_speed):
        # 格式化速度显示
        def format_speed(speed):
            if speed < 1024:
                return f"{speed:.1f} B/s"
            elif speed < 1024 * 1024:
                return f"{speed/1024:.1f} KB/s"
            else:
                return f"{speed/(1024*1024):.1f} MB/s"
        
        # 更新界面标签
        self.upload_label.config(text=format_speed(upload_speed))
        self.download_label.config(text=format_speed(download_speed))
        
        # 更新总流量显示
        self.total_upload_label.config(text=self.format_total_traffic(self.total_upload))
        self.total_download_label.config(text=self.format_total_traffic(self.total_download))

    
                # 确定系统类型和下载文件名
        system_suffix = "Darwin" if self.os_type == "Darwin" else "Windows"
        filename = f"NetFucker_{system_suffix}.zip"
        download_path = os.path.join(os.path.expanduser("~"), "Downloads", filename)
                
                # 默认下载源列表
        urls = [
                    f"https://github.com/Michaelwucoc/SHBS-NetFucker/releases/download/{version}/{filename}",
                    f"https://mirror.ghproxy.com/https://github.com/Michaelwucoc/SHBS-NetFucker/releases/download/{version}/{filename}"
                ]
            

    
    def handle_download_complete(self, message, download_path):
        if messagebox.askyesno("安装更新", message):
            # 打开文件所在目录
            if self.os_type == "Darwin":
                subprocess.run(['open', '-R', download_path])
            else:
                subprocess.run(['explorer', '/select,', download_path])
    
    def show_update_options(self, version):
        # 创建更新选项窗口
        update_window = tk.Toplevel(self.root)
        update_window.title("更新选项")
        update_window.geometry("200x300")
        update_window.transient(self.root)
        update_window.grab_set()
        
        # 配置窗口
        frame = ttk.Frame(update_window, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        update_window.grid_columnconfigure(0, weight=1)
        
        # 更新信息
        ttk.Label(frame, text=f"发现新版本: {version}", font=("Helvetica", 12, "bold")).grid(row=0, column=0, pady=10)
        ttk.Label(frame, text="请选择下载方式：").grid(row=1, column=0, pady=5)
        
        def open_mirror():
            system_suffix = "Darwin" if self.os_type == "Darwin" else "Windows"
            filename = f"NetFucker_{system_suffix}.zip"
            url = f"https://github.shbs.club/https://github.com/Michaelwucoc/SHBS-NetFucker/releases/download/{version}/{filename}"
            webbrowser.open(url)
            update_window.destroy()
        
        def open_official():
            system_suffix = "Darwin" if self.os_type == "Darwin" else "Windows"
            filename = f"NetFucker_{system_suffix}.zip"
            url = f"https://github.com/Michaelwucoc/SHBS-NetFucker/releases/download/{version}/{filename}"
            webbrowser.open(url)
            update_window.destroy()
        
        ttk.Button(frame, text="使用镜像站下载", command=open_mirror).grid(row=2, column=0, pady=10, padx=20, sticky=tk.EW)
        ttk.Button(frame, text="使用官方源下载", command=open_official).grid(row=3, column=0, pady=10, padx=20, sticky=tk.EW)
        
        # 取消按钮
        ttk.Button(frame, text="取消", command=update_window.destroy).grid(row=4, column=0, pady=10, padx=20, sticky=tk.EW)

    def check_update(self):
        def update_gui(state, text):
            self.check_update_button.config(state=state)
            self.latest_version_label.config(text=text)
        
        def handle_update_result(success, version=None, error=None):
            if success:
                if version != self.current_version:
                    # 检查是否已经存在更新窗口
                    for widget in self.root.winfo_children():
                        if isinstance(widget, tk.Toplevel) and widget.wm_title() == "更新选项":
                            widget.lift()
                            return
                    # 如果不存在更新窗口，则创建一个
                    self.show_update_options(version)
                else:
                    self.log("当前已是最新版本")
            else:
                self.log(f"检查更新错误: {error}")
            
            # 恢复按钮状态
            self.root.after(0, lambda: update_gui('normal', f"最新版本: {version if version else '检查失败'}"))
        
        try:
            # 禁用更新按钮
            self.root.after(0, lambda: update_gui('disabled', "最新版本: 检查中..."))
            
            # 获取GitHub最新release版本
            api_url = "https://api.github.com/repos/Michaelwucoc/SHBS-NetFucker/releases/latest"
            self.log(f"正在从{api_url}获取最新版本信息...")
            response = requests.get(api_url, timeout=15)
            
            if response.status_code == 200:
                release_info = response.json()
                latest_version = release_info['tag_name']
                self.log(f"获取到最新版本: {latest_version}")
                self.root.after(0, lambda: handle_update_result(True, latest_version))
            else:
                error_msg = f"获取版本信息失败: HTTP {response.status_code}"
                self.log(error_msg)
                self.root.after(0, lambda: handle_update_result(False, error=error_msg))
            
            if response.status_code == 200:
                release_info = response.json()
                latest_version = release_info['tag_name']
                self.root.after(0, lambda: handle_update_result(True, latest_version))
            else:
                self.root.after(0, lambda: handle_update_result(False, error=f"HTTP {response.status_code}"))
                
        except Exception as e:
            self.root.after(0, lambda: handle_update_result(False, error=str(e)))

        finally:
            self.check_update_button.config(state='normal')
    
    def run(self):
        self.root.mainloop()

    def format_speed(self, bytes_per_sec):
        if bytes_per_sec >= 1024 * 1024:
            return f"{bytes_per_sec / (1024 * 1024):.2f} MB/s"
        elif bytes_per_sec >= 1024:
            return f"{bytes_per_sec / 1024:.2f} KB/s"
        else:
            return f"{bytes_per_sec:.2f} B/s"

    def format_total_traffic(self, bytes_total):
        if bytes_total >= 1024 * 1024 * 1024:
            return f"{bytes_total / (1024 * 1024 * 1024):.2f} GB"
        elif bytes_total >= 1024 * 1024:
            return f"{bytes_total / (1024 * 1024):.2f} MB"
        elif bytes_total >= 1024:
            return f"{bytes_total / 1024:.2f} KB"
        else:
            return f"{bytes_total:.2f} B"

    def report_traffic(self):
        try:
            current_time = time.time()
            # 每5分钟上报一次数据
            if current_time - self.last_report_time >= 300:
                mac = self.mac_label.cget("text")
                ip = self.ip_label.cget("text")
                
                data = {
                    'mac_address': mac,
                    'ip_address': ip,
                    'total_upload': self.total_upload,
                    'total_download': self.total_download
                }
                
                try:
                    response = requests.post(
                        'http://localhost:3000/report',
                        json=data,
                        timeout=5
                    )
                    
                    if response.status_code == 200:
                        self.log("流量数据上报成功")
                    else:
                        self.log(f"流量数据上报失败: HTTP {response.status_code}")
                except:
                    self.log("流量数据上报失败: 无法连接到服务器")
                
                self.last_report_time = current_time
        except Exception as e:
            self.log(f"流量数据上报错误: {str(e)}")

    def monitor_traffic(self):
        last_bytes_sent = 0
        last_bytes_recv = 0
        while True:
                try:
                    if self.os_type == "Windows":
                        # Windows系统使用性能计数器获取网络流量
                        result = subprocess.run(
                            ['powershell', '-Command', 
                             "Get-Counter '\\Network Interface(*)\\Bytes Sent/sec','\\Network Interface(*)\\Bytes Received/sec'"],
                            capture_output=True, text=True)
                        if result.returncode == 0:
                            lines = result.stdout.split('\n')
                            bytes_sent = 0
                            bytes_recv = 0
                            for line in lines:
                                if 'Bytes Sent' in line:
                                    try:
                                        bytes_sent = float(line.split(':')[-1].strip())
                                    except:
                                        pass
                                elif 'Bytes Received' in line:
                                    try:
                                        bytes_recv = float(line.split(':')[-1].strip())
                                    except:
                                        pass
                    else:
                        # macOS系统使用netstat命令获取网络流量
                        result = subprocess.run(
                            ['netstat', '-I', 'en0', '-b'],
                            capture_output=True, text=True)
                        if result.returncode == 0:
                            lines = result.stdout.split('\n')
                            if len(lines) > 1:
                                try:
                                    fields = lines[1].split()
                                    bytes_recv = int(fields[6])
                                    bytes_sent = int(fields[9])
                                except:
                                    bytes_recv = 0
                                    bytes_sent = 0
                        else:
                            bytes_recv = 0
                            bytes_sent = 0
                    
                    if last_bytes_sent > 0 and last_bytes_recv > 0:
                        upload_speed = bytes_sent - last_bytes_sent
                        download_speed = bytes_recv - last_bytes_recv
                        
                        # 确保速度不为负数
                        upload_speed = max(0, upload_speed)
                        download_speed = max(0, download_speed)
                        
                        # 更新总流量
                        self.total_upload += upload_speed
                        self.total_download += download_speed
                        
                        # 更新界面显示
                        self.root.after(0, lambda: self.upload_label.config(
                            text=self.format_speed(upload_speed)))
                        self.root.after(0, lambda: self.download_label.config(
                            text=self.format_speed(download_speed)))
                        self.root.after(0, lambda: self.total_upload_label.config(
                            text=self.format_total_traffic(self.total_upload)))
                        self.root.after(0, lambda: self.total_download_label.config(
                            text=self.format_total_traffic(self.total_download)))
                        
                        # 上报流量数据
                        self.report_traffic()
                    
                    last_bytes_sent = bytes_sent
                    last_bytes_recv = bytes_recv
                    
                except Exception as e:
                    self.log(f"获取网络流量数据失败: {str(e)}")
                    # 重置计数器
                    last_bytes_sent = 0
                    last_bytes_recv = 0
                
                time.sleep(1)
        
        # 初始化流量统计变量
        self.total_upload = 0
        self.total_download = 0
        self.last_report_time = time.time()
        
        # 启动流量监控线程
        threading.Thread(target=self.monitor_traffic, daemon=True).start()

if __name__ == "__main__":
    app = NetFucker()
    app.run()