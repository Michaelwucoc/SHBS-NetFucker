// 当前版本号
const CURRENT_VERSION = "v20250307_01";

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    // 初始化版本信息
    document.getElementById('current-version').textContent = `当前版本: ${CURRENT_VERSION}`;
    
    // 获取系统信息
    initSystemInfo();
    
    // 绑定按钮事件
    document.getElementById('login').addEventListener('click', login);
    document.getElementById('check-update').addEventListener('click', checkUpdate);
    document.getElementById('close-modal').addEventListener('click', () => {
        document.getElementById('update-modal').style.display = 'none';
    });
    document.getElementById('mirror-download').addEventListener('click', () => downloadUpdate('mirror'));
    document.getElementById('official-download').addEventListener('click', () => downloadUpdate('official'));
    
    // 初始检查更新
    checkUpdate();
    
    // 初始网络检测
    checkWifiConnection();
});

// 初始化系统信息
async function initSystemInfo() {
    // 获取操作系统信息
    const userAgent = navigator.userAgent;
    let osInfo = 'Unknown';
    if (/iPhone|iPad|iPod/.test(userAgent)) {
        osInfo = 'iOS';
    } else if (/Android/.test(userAgent)) {
        osInfo = 'Android';
    } else if (/Mac/.test(userAgent)) {
        osInfo = 'macOS';
    } else if (/Windows/.test(userAgent)) {
        osInfo = 'Windows';
    } else if (/Linux/.test(userAgent)) {
        osInfo = 'Linux';
    }
    document.getElementById('os-info').textContent = osInfo;
}

// 检查WiFi连接状态
async function checkWifiConnection() {
    // 使用navigator.onLine检查基本网络连接
    const isOnline = navigator.onLine;
    
    if (!isOnline) {
        log('请检查网络连接');
        updateStatus('请检查网络连接', '#dc3545');
        return false;
    }
    
    // 添加网络状态监听器
    window.addEventListener('online', () => {
        log('网络已连接');
        updateStatus('网络已连接', '#28a745');
    });
    
    window.addEventListener('offline', () => {
        log('网络已断开');
        updateStatus('网络已断开', '#dc3545');
    });
    
    // 假设连接成功
    log('检测到网络连接');
    updateStatus('网络已连接', '#28a745');
    return true;
}

// 登录
async function login() {
    // 首先检查是否连接到wlan-teacher
    if (!await checkWifiConnection()) {
        return;
    }

    const button = document.getElementById('login');
    button.disabled = true;
    updateStatus('登录中...', '#666666');
    
    try {
        const loginData = {
            userName: 'tempstu',
            userPwd: 'c2hiczIwMjU=', // Base64编码的密码
            userip: 'null',
            usermac: 'null',
            wlanssid: 'wlan-teacher',
            language: 'English',
            portalProxyIP: '172.16.1.4',
            portalProxyPort: '50200',
            dcPwdNeedEncrypt: '1',
            assignIpType: '0',
            appRootUrl: 'http://172.16.1.4:8080/portal/'
        };
        
        // 确保使用 HTTP 协议
        const loginUrl = 'http://172.16.1.4:8080/portal/pws?t=li';
        log(`发送登录请求: ${loginUrl}`);
        
        const loginResponse = await fetch(loginUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest'
            },
            mode: 'no-cors',  // 使用 no-cors 模式
            credentials: 'omit',
            body: new URLSearchParams(loginData)
        });
        
        log(`登录请求已发送`);
        
        // 由于使用no-cors模式，我们无法读取响应内容
        // 但是如果请求没有抛出错误，我们认为登录可能成功
        updateStatus('可能已登录成功', '#28a745');
        log('登录请求已完成');
        log('==================================');
        log('Thank you for using Milk NetFucker.');
        log('Official Website: net.shbs.club');
        log('==================================');
        
        // 登录完成后检测网络状态和更新
        checkNetworkStatus(3);
        checkUpdate();
    } catch (error) {
        log(`登录错误: ${error.message}`);
        updateStatus('登录错误', '#dc3545');
    } finally {
        button.disabled = false;
    }
}

// 检查网络状态
async function checkNetworkStatus(times = 1) {
    let successCount = 0;
    let totalLatency = 0;
    // 确保使用 HTTP 协议
    const testUrl = 'http://172.16.1.4:8080/portal/';
    
    // 首先检查基本网络连接
    if (!navigator.onLine) {
        log('网络已断开');
        updateStatus('网络已断开', '#dc3545');
        return false;
    }
    
    for (let i = 0; i < times; i++) {
        try {
            const startTime = performance.now();
            const response = await fetch(testUrl, { 
                mode: 'no-cors',
                cache: 'no-cache',
                headers: {
                    'Pragma': 'no-cache'
                }
            });
            const endTime = performance.now();
            const latency = endTime - startTime;
            
            // 在no-cors模式下，我们无法读取response.ok，所以只要请求没有抛出错误就认为成功
            successCount++;
            totalLatency += latency;
            log(`网络检测 #${i+1}: 成功 - 延迟: ${latency.toFixed(2)}ms`);
            
            await new Promise(resolve => setTimeout(resolve, 1000));
        } catch (error) {
            log(`网络检测 #${i+1}: 错误 - ${error.message}`);
        }
    }
    
    if (successCount >= times/2) {
        const avgLatency = totalLatency / successCount;
        const statusText = `已连接到因特网 (平均延迟: ${avgLatency.toFixed(2)}ms)`;
        updateStatus(statusText, '#28a745');
        return true;
    } else {
        updateStatus('未连接', '#dc3545');
        return false;
    }
}

// 检查更新
async function checkUpdate() {
    const button = document.getElementById('check-update');
    const versionLabel = document.getElementById('latest-version');
    button.disabled = true;
    versionLabel.textContent = '最新版本: 检查中...';
    
    try {
        const apiUrl = 'https://api.github.com/repos/Michaelwucoc/SHBS-NetFucker/releases/latest';
        log(`正在从${apiUrl}获取最新版本信息...`);
        
        const response = await fetch(apiUrl);
        if (response.ok) {
            const releaseInfo = await response.json();
            const latestVersion = releaseInfo.tag_name;
            log(`获取到最新版本: ${latestVersion}`);
            
            if (latestVersion !== CURRENT_VERSION) {
                showUpdateModal(latestVersion);
            } else {
                log('当前已是最新版本');
            }
            
            versionLabel.textContent = `最新版本: ${latestVersion}`;
        } else {
            throw new Error(`HTTP ${response.status}`);
        }
    } catch (error) {
        log(`检查更新错误: ${error.message}`);
        versionLabel.textContent = '最新版本: 检查失败';
    } finally {
        button.disabled = false;
    }
}

// 显示更新对话框
function showUpdateModal(version) {
    document.getElementById('update-version').textContent = `发现新版本: ${version}`;
    document.getElementById('update-modal').style.display = 'block';
}

// 下载更新
function downloadUpdate(source) {
    const systemSuffix = /iPhone|iPad|iPod/.test(navigator.userAgent) ? 'iOS' :
                        /Android/.test(navigator.userAgent) ? 'Android' :
                        /Mac/.test(navigator.userAgent) ? 'Darwin' : 'Windows';
    
    const filename = `NetFucker_${systemSuffix}.zip`;
    const version = document.getElementById('latest-version').textContent.split(': ')[1];
    const baseUrl = source === 'mirror' ? 
        'https://github.shbs.club/https://github.com/Michaelwucoc/SHBS-NetFucker/releases/download' :
        'https://github.com/Michaelwucoc/SHBS-NetFucker/releases/download';
    
    const downloadUrl = `${baseUrl}/${version}/${filename}`;
    window.open(downloadUrl);
    document.getElementById('update-modal').style.display = 'none';
}

// 更新状态显示
function updateStatus(text, color) {
    const statusElement = document.getElementById('network-status');
    statusElement.textContent = text;
    statusElement.style.color = color;
}

// 添加日志
function log(message) {
    const logContainer = document.getElementById('log-container');
    const timestamp = new Date().toLocaleString();
    logContainer.innerHTML += `${timestamp} ${message}\n`;
    logContainer.scrollTop = logContainer.scrollHeight;
}