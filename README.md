# 萝卜特 - 基于 NapCat 的企鹅机器人

## 使用方法

### 1. 部署 NapCat

参考 [NapCat 官方文档](https://napcat.napneko.icu/) 部署。

新建一个 HTTP 服务端和一个 HTTP 客户端，记好 HTTP 服务端的 Token

HTTP 客户端地址需要与 `.env` 文件中的地址端口一致

```
http://{HTTP_HOST}:{HTTP_PORT}
```

### 2.设置环境变量

复制 `.env.example` 并重命名为 `.env` 并填写必要的环境变量。

```
ONEBOT_TOKEN=your-onebot-token # 填写 Napcat 服务端的 Token
ONEBOT_HOST=http://your-onebot-host:port # 填写 Napcat 服务端的地址与端口

HTTP_HOST=0.0.0.0 # 填写 HTTP 服务端的地址
HTTP_PORT=8080 # 填写 HTTP 服务端的端口

BOT_NAME=萝卜特特 # 填写机器人的名称

ADMIN_QID=10001 # 填写管理员 QID
```


### 手动启动

```bash
cd backend

pip install -r requirements.txt

python main.py
```

### Docker-Compose

```cmd
docker-compose up -d
```