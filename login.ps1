# 获取MAC地址
$mac = (Get-WmiObject win32_networkadapterconfiguration | Where-Object { $_.IPEnabled -eq $true } | Select-Object -First 1).MACAddress
$mac = $mac.Replace(':', '-')

# 获取IP地址
$ip = (Get-NetIPAddress | Where-Object { $_.AddressFamily -eq 'IPv4' -and $_.PrefixOrigin -eq 'Dhcp' } | Select-Object -First 1).IPAddress

# 初始化请求URL
$initUrl = "http://172.16.1.4:8080/portal/?wlanusermac=$mac&wlanuserip=$ip&wlanacname=AC&ssid=wlan-teacher"

# 发送初始化请求
Invoke-WebRequest -Uri $initUrl -Method Get

# 准备登录数据
$loginData = @{
    userName = 'tempstu'
    userPwd = 'c2hiczIwMjU='
    userip = $ip
    usermac = 'null'
    wlanssid = 'wlan-teacher'
    language = 'English'
    portalProxyIP = '172.16.1.4'
    portalProxyPort = '50200'
    dcPwdNeedEncrypt = '1'
    assignIpType = '0'
    appRootUrl = 'http://172.16.1.4:8080/portal/'
}

# 设置请求头
$headers = @{
    'Content-Type' = 'application/x-www-form-urlencoded; charset=UTF-8'
    'X-Requested-With' = 'XMLHttpRequest'
}

# 发送登录请求
$loginUrl = 'http://172.16.1.4:8080/portal/pws?t=li'
try {
    $response = Invoke-WebRequest -Uri $loginUrl -Method Post -Body $loginData -Headers $headers
    if ($response.StatusCode -eq 200) {
        Write-Host "登录成功"
    } else {
        Write-Host "登录失败"
    }
} catch {
    Write-Host "登录错误: $_"
}