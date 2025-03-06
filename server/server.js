const express = require('express');
const http = require('http');
const WebSocket = require('ws');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());

const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

// 存储在线用户信息
const onlineUsers = new Map();

// WebSocket连接处理
wss.on('connection', (ws) => {
    ws.on('message', (message) => {
        try {
            const data = JSON.parse(message);
            if (data.type === 'init') {
                // 初始化连接
                onlineUsers.set(data.mac_address, {
                    ip: data.ip_address,
                    upload: 0,
                    download: 0,
                    lastUpdate: Date.now(),
                    ws: ws
                });
                broadcastStats();
            } else if (data.type === 'traffic_update') {
                // 更新流量数据
                const user = onlineUsers.get(data.mac_address);
                if (user) {
                    user.upload = data.total_upload;
                    user.download = data.total_download;
                    user.lastUpdate = Date.now();
                    broadcastStats();
                }
            }
        } catch (e) {
            console.error('Error processing message:', e);
        }
    });

    ws.on('close', () => {
        // 清理断开连接的用户
        for (const [mac, user] of onlineUsers.entries()) {
            if (user.ws === ws) {
                onlineUsers.delete(mac);
                broadcastStats();
                break;
            }
        }
    });
});

// 定期清理超时连接（5分钟无更新视为离线）
setInterval(() => {
    const now = Date.now();
    for (const [mac, user] of onlineUsers.entries()) {
        if (now - user.lastUpdate > 5 * 60 * 1000) {
            onlineUsers.delete(mac);
            broadcastStats();
        }
    }
}, 60 * 1000);

// 广播统计信息
function broadcastStats() {
    const stats = {
        online_count: onlineUsers.size,
        total_upload: 0,
        total_download: 0,
        users: []
    };

    for (const [mac, user] of onlineUsers.entries()) {
        stats.total_upload += user.upload;
        stats.total_download += user.download;
        stats.users.push({
            mac_address: mac,
            ip_address: user.ip,
            upload: user.upload,
            download: user.download
        });
    }

    const message = JSON.stringify(stats);
    wss.clients.forEach(client => {
        if (client.readyState === WebSocket.OPEN) {
            client.send(message);
        }
    });
}

// HTTP API
app.post('/report', (req, res) => {
    const { mac_address, ip_address, total_upload, total_download } = req.body;
    const user = onlineUsers.get(mac_address);
    
    if (user) {
        user.upload = total_upload;
        user.download = total_download;
        user.lastUpdate = Date.now();
        broadcastStats();
    }
    
    res.json({ status: 'success' });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});