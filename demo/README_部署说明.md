# 部署说明文档

## 快速部署（推荐）

双击运行 `deploy.bat` 即可自动完成部署和启动。

---

## 手动部署步骤

### 1. 环境要求

- Python 3.8 或更高版本
- Windows 10/11

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置防火墙

以管理员身份运行命令提示符，执行：

```bash
netsh advfirewall firewall add rule name="FastAPI 8000" dir=in action=allow protocol=TCP localport=8000
```

### 4. 启动服务

```bash
python main.py
```

或使用 uvicorn：

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 访问方式

| 设备类型 | 访问地址 |
|---------|---------|
| 本机 | http://localhost:8000 |
| 局域网其他设备 | http://10.10.20.200:8000 |

---

## 安全配置

### 默认账号

- **用户名**: `admin`
- **密码**: `admin123`

### 修改密码

编辑 `main.py` 文件，找到以下行：

```python
VALID_USERS = {
    "admin": "admin123",  # 修改为你的强密码
    "user": "user123"
}
```

### 添加新用户

在 `VALID_USERS` 字典中添加：

```python
VALID_USERS = {
    "admin": "admin123",
    "user1": "password1",
    "user2": "password2"
}
```

---

## 高级配置

### 使用 Nginx 反向代理（HTTPS 支持）

1. 安装 Nginx for Windows
2. 复制 `nginx.conf` 到 Nginx 配置目录
3. 修改配置中的 IP 地址
4. 启动 Nginx

### CORS 配置

编辑 `main.py` 中的 CORS 设置：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://10.10.20.200:8000",  # 添加允许的 IP
        "http://localhost:8000"
    ],
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type"],
)
```

---

## 故障排除

### 无法访问服务

1. 检查防火墙是否开放 8000 端口
2. 确认服务正在运行
3. 检查 IP 地址是否正确

### 依赖安装失败

```bash
# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 端口被占用

修改启动端口：

```bash
uvicorn main:app --host 0.0.0.0 --port 8001
```

然后访问 `http://10.10.20.200:8001`

---

## 停止服务

按 `Ctrl + C` 停止服务。

---

## 数据备份

数据库文件位于：`business_data.db`

定期备份此文件以防数据丢失。
