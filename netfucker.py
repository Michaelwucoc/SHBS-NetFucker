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

class NetFucker:
    def __init__(self):
        self.root = tk.Tk()
        self.current_version = "v20250306"
        self.root.title(f"SHBS NetFucker {self.current_version}")
        self.root.geometry("500x600")
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
        
        # 系统信息显示
        ttk.Label(self.main_frame, text="操作系统:").grid(row=0, column=0, sticky=tk.W)
        self.os_label = ttk.Label(self.main_frame, text=f"{self.os_type}")
        self.os_label.grid(row=0, column=1, sticky=tk.W)
        
        # MAC地址显示
        ttk.Label(self.main_frame, text="MAC地址:").grid(row=1, column=0, sticky=tk.W)
        self.mac_label = ttk.Label(self.main_frame, text="获取中...")
        self.mac_label.grid(row=1, column=1, sticky=tk.W)
        
        # IP地址显示
        ttk.Label(self.main_frame, text="IP地址:").grid(row=2, column=0, sticky=tk.W)
        self.ip_label = ttk.Label(self.main_frame, text="获取中...")
        self.ip_label.grid(row=2, column=1, sticky=tk.W)
        
        # 网络状态显示
        ttk.Label(self.main_frame, text="网络状态:").grid(row=3, column=0, sticky=tk.W)
        self.status_label = ttk.Label(self.main_frame, text="未登录", foreground="#666666")
        self.status_label.grid(row=3, column=1, sticky=tk.W)
        
        # 连接网络按钮
        self.connect_button = ttk.Button(self.main_frame, text="连接网络", command=self.connect_wifi, style='Custom.TButton')
        self.connect_button.grid(row=4, column=0, pady=5)
        
        # 登录按钮
        self.login_button = ttk.Button(self.main_frame, text="登录", command=self.login, style='Custom.TButton')
        self.login_button.grid(row=4, column=1, pady=5)
        
        # 版本信息显示
        version_frame = ttk.Frame(self.main_frame)
        version_frame.grid(row=5, column=0, columnspan=2, pady=5)
        
        self.version_label = ttk.Label(version_frame, text=f"当前版本: {self.current_version}", foreground="#666666")
        self.version_label.pack(side=tk.LEFT, padx=5)
        
        self.latest_version_label = ttk.Label(version_frame, text="最新版本: 检查中...", foreground="#666666")
        self.latest_version_label.pack(side=tk.LEFT, padx=5)
        
        self.check_update_button = ttk.Button(version_frame, text="检查更新", command=self.check_update)
        self.check_update_button.pack(side=tk.LEFT, padx=5)
        
        # 网络提示信息
        self.network_hint = ttk.Label(self.main_frame, text="如果无法登陆，请连接到wlan-teacher网络", foreground="#666666")
        self.network_hint.grid(row=6, column=0, columnspan=2, pady=5)
        
        # 日志显示区域
        log_frame = ttk.LabelFrame(self.main_frame, text="运行日志", padding="5")
        log_frame.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=50)
        self.log_text.pack(expand=True, fill='both')
        self.log_text.configure(font=('Courier', 10))
        
        # 配置日志区域的网格权重
        self.main_frame.grid_rowconfigure(7, weight=1)
        
        # 初始检查更新
        threading.Thread(target=self.check_update, daemon=True).start()
        
        # 初始化系统信息
        self.init_system_info()
        
        # 执行初始网络检测
        self.check_network_status(3)
    
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
            status_text = f"已连接 (平均延迟: {avg_latency:.2f}ms)"
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

    
    def check_update(self):
        def update_gui(state, text):
            self.check_update_button.config(state=state)
            self.latest_version_label.config(text=text)
        
        def handle_update_result(success, version=None, error=None):
            if success:
                if version != self.current_version:
                    message = f"发现新版本 {version}\n\n是否前往下载页面？"
                    if messagebox.askyesno("更新提示", message):
                        webbrowser.open(f"https://github.com/Michaelwucoc/SHBS-NetFucker/releases/tag/{version}")
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
            response = requests.get(
                "https://api.github.com/repos/Michaelwucoc/SHBS-NetFucker/releases/latest",
                timeout=15
            )
            
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

if __name__ == "__main__":
    app = NetFucker()
    app.run()