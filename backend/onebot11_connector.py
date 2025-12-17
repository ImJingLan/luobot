import json
import requests
import logging
import os
from dotenv import load_dotenv

load_dotenv("../.env")

logger = logging.getLogger("OneBot Connector")
logger.setLevel(logging.INFO)

# 创建文件handler
file_handler = logging.FileHandler("./logs/onebot_connector.log")
file_handler.setLevel(logging.INFO)

# 设置日志格式
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# 添加handlers到logger
if not logger.handlers:  # 避免重复添加handlers
    logger.addHandler(file_handler)

# 配置Flask不记录详细的访问日志（可选）
logging.getLogger('werkzeug').setLevel(logging.WARNING)

onebotHost = os.environ.get("ONEBOT_HOST", "http://napcat:3000")  # 默认值，可通过环境变量 ONEBOT_HOST 修改
onebotToken = os.environ.get("ONEBOT_TOKEN", "123456")  # 默认值，可通过环境变量 ONEBOT_TOKEN 修改

# Create headers dynamically to use the latest token
def get_headers():
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {onebotToken}"
    }


def send_group_msg(message, group_id):
    url = f"{onebotHost}/send_group_msg"
    data = json.dumps({"message": message, "group_id": group_id})
    requestsBody = requests.post(url, data=data, headers=get_headers())
    logger.info(f"Sent message: {message} to group {group_id}")
    return requestsBody


def send_private_msg(message, user_id):
    url = f"{onebotHost}/send_private_msg"
    data = json.dumps({"message": message, "user_id": user_id})
    requestsBody = requests.post(url, data=data, headers=get_headers())
    logger.info(f"Sent message: {message} to user {user_id}")
    return requestsBody


def send_like(user_id, times):
    url = f"{onebotHost}/send_like"
    data = json.dumps({"user_id": user_id, "times": times})
    requestsBody = requests.post(url, data=data, headers=get_headers())
    logger.info(f"Sent {times} likes to user {user_id}")
    return requestsBody


def set_qq_nickname(nickname):
    url = f"{onebotHost}/set_qq_profile"
    data = json.dumps({"nickname": nickname})
    requestsBody = requests.post(url, data=data, headers=get_headers())
    logger.info(f"Set QQ nickname: nickname={nickname}")
    return requestsBody


def set_qq_personal_note(personal_note):
    url = f"{onebotHost}/set_qq_profile"
    data = json.dumps({"personal_note": personal_note})
    requestsBody = requests.post(url, data=data, headers=get_headers())
    logger.info(f"Set QQ personal note: personal_note={personal_note}")
    return requestsBody


def set_self_longnick(longNick):
    url = f"{onebotHost}/set_qq_profile"
    data = json.dumps({"longNick": longNick})
    requestsBody = requests.post(url, data=data, headers=get_headers())
    logger.info(f"Set QQ longNick: longNick={longNick}")
    return requestsBody

def get_login_info():
    url = f"{onebotHost}/get_login_info"
    requestsBody = requests.post(url, headers=get_headers())
    logger.info(f"Get login info")
    return requestsBody
