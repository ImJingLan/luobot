from venv import logger
from flask import Flask, request, request_started
import json
import requests
import logging
from jrrp import get_jrrp,check_user_consent, add_user_consent, remove_user_consent
from onebot11_connector import send_group_msg, send_like, send_private_msg, set_qq_nickname, set_qq_personal_note, set_self_longnick,get_login_info
import re
import random
import os
from dotenv import load_dotenv

logger = logging.getLogger("BotLuo")
logger.setLevel(logging.INFO)

# 创建文件handler
file_handler = logging.FileHandler("./logs/chatbot.log", encoding='utf-8')
file_handler.setLevel(logging.INFO)

# 创建控制台handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# 设置日志格式
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# 添加handlers到logger
if not logger.handlers:  # 避免重复添加handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

# 配置Flask不记录详细的访问日志（可选）
logging.getLogger('werkzeug').setLevel(logging.WARNING)

# 从环境变量中读取onebot配置，使用默认值作为 fallback

onebotHost = os.environ.get("ONEBOT_HOST", "http://127.0.0.1:3000")  # 默认值，可通过环境变量 ONEBOT_HOST 修改
onebotToken = os.environ.get("ONEBOT_TOKEN", "123456")  # 默认值，可通过环境变量 ONEBOT_TOKEN 修改

ADMIN_QID = int(os.environ.get("ADMIN_QID", 10000))  # 默认值，可通过环境变量 ADMIN_QID 修改

BOT_NAME = os.environ.get("BOT_NAME", "Robot")  # 默认值，可通过环境变量 BOT_NAME 修改

app = Flask(__name__)

def get_bot_qid():
    login_info = get_login_info()
    if login_info.status_code == 200:
        login_info_json = login_info.json()
    return login_info_json["data"]["user_id"]

BOT_QID = get_bot_qid() # 获取机器人 QID

def isUcoc(command):
    pattern = re.compile(r'(?<![a-zA-Z])(undercut|overcut|ucoc)(?![a-zA-Z])')
    match = pattern.search(command)
    return bool(match)


def isStroll(command):
    pattern = re.compile(r'(?<![a-zA-Z])(Str|少爷|斯特罗尔|Stroll)(?![a-zA-Z])')
    match = pattern.search(command)
    return bool(match)

def is_at_message(message):
    if not message:
        return False
    return message.startswith(f'[CQ:at,qq={BOT_QID}]')


def get_content_after_at(message):
    if not is_at_message(message):
        return ""
    at_pattern = f"[CQ:at,qq={BOT_QID}] "
    if message.startswith(at_pattern):
        return message[len(at_pattern):]
    return message[len(f'[CQ:at,qq={BOT_QID}] '):]


# 定义今日人品免责声明内容
JRRP_DISCLAIMER = '''【今日人品功能免责声明】

1. 今日人品功能仅供娱乐，生成的数值完全随机，不代表真实的运气、能力或其他任何实际意义。
2. 请勿将人品数值作为任何决策的依据，尤其是重要的学习、工作或生活决策。
3. 我们不对因使用此功能而产生的任何心理影响或行为后果负责。
4. 你可以随时使用“@萝卜特特 拒绝jrrp免责声明”来拒绝。
5. 使用本功能即表示您理解并同意以上条款。

“@萝卜特特 同意jrrp免责声明" 以使用今日人品功能。

如您不同意上述条款，请忽略该功能或使用“@萝卜特特 拒绝jrrp免责声明”来拒绝。'''


@app.route('/', methods=['POST', 'GET'])
def receive_json():
    json_data = request.get_json()
    # print(json_data)
    if json_data["post_type"] == "message":

        if "raw_message" in json_data:
            raw_message = json_data["raw_message"]
            message_id = json_data["message_id"]

            if json_data['message_type'] == 'private':

                if json_data['sender']['user_id'] == ADMIN_QID:
                    logger.info(
                        f"收到来自管理员 {json_data['sender']['nickname']} ({json_data['sender']['user_id']}) 的私信: {json_data['raw_message']}"
                    )
                    if raw_message.startswith("你叫"):
                        nickname = raw_message[2:]
                        set_qq_nickname(nickname)
                        send_private_msg(
                            f"[CQ:reply,id={message_id}] 我已将昵称设置为 {nickname}",
                            json_data['sender']['user_id'])
                        logger.info(
                            f"管理员 {json_data['sender']['nickname']} ({json_data['sender']['user_id']}) 设置了 QQ 昵称: {nickname}"
                        )
                    if raw_message.startswith("你的简介是"):
                        personal_note = raw_message[5:]
                        set_qq_personal_note(personal_note)
                        send_private_msg(
                            f"[CQ:reply,id={message_id}] 我已将简介设置为 {personal_note}",
                            json_data['sender']['user_id'])
                        logger.info(
                            f"管理员 {json_data['sender']['nickname']} ({json_data['sender']['user_id']}) 设置了 QQ 简介: {personal_note}"
                        )
                    if raw_message.startswith("你的签名是"):
                        longNick = raw_message[5:]
                        set_self_longnick(longNick)
                        send_private_msg(
                            f"[CQ:reply,id={message_id}] 我已将个性签名设置为 {longNick}",
                            json_data['sender']['user_id'])
                        logger.info(
                            f"管理员 {json_data['sender']['nickname']} ({json_data['sender']['user_id']}) 设置了 QQ 个性签名: {longNick}"
                        )

                else:
                    logger.info(
                        f"收到来自 {json_data['sender']['nickname']} ({json_data['sender']['user_id']}) 的私信: {json_data['raw_message']}"
                    )
                    send_private_msg(f"[CQ:reply,id={message_id}] 请在群组中使唤{BOT_NAME}",
                                     json_data['sender']['user_id'])
                    logger.info(
                        f"回复 {json_data['sender']['nickname']} ({json_data['sender']['user_id']}) 私信: [CQ:reply,id={message_id}] 请在群组中使唤萝卜特"
                    )

            if json_data['message_type'] == 'group':

                if isUcoc(raw_message):
                    ucoc = '''主播主播，什么是Undercut，什么是Overcut？🤪🤪🤪
所谓Undercut Overcut 是指利用进站完成的超车的策略。🥰🥰🥰

所谓的 Undercut 指的是利用早进站让自己的排名先 Under ⬇️
然后用新胎做出很快的圈速
在对手完成换胎出站之后排在对手前面完成超车🤓🤓🤓

所谓的 Overcut 指的是在对手进站后依然留在赛道上
 own排名先 Over
然后用旧胎做出比对手更快的圈速
在自己进站之后出站排在对手的前面完成超车。💪😅💪😅'''
                    sendMsgBody = send_group_msg(f"{ucoc}",
                                                 json_data['group_id'])
                    logger.info(f"发送 UCOC 到 lzgz洗浴中心")

                elif (isStroll(raw_message)):
                    stroll = [
                        "班加罗尔", "加刚特尔", "斯图加特", "卡斯特罗", "兰卡斯特", "斯里兰卡", "卡卡罗特",
                        "托尔斯泰", "兰斯洛特", "罗斯托夫", "托洛茨基", "图马斯特", "斯莱特林", "斯图雷登",
                        "司马相如", "司马仲达", "斯图尔特", "鸿星尔克", "提亚马特", "菲尔普斯", "阿拉斯加",
                        "直布罗陀", "斯威夫特", "威斯康星", "德克萨斯", "诺克萨斯", "格雷福斯", "特朗德尔",
                        "科罗拉多", "危地马拉", "马拉内罗", "托斯卡纳", "拉布拉多", "斯琴高娃", "派拉斯特",
                        "阿泰斯特", "瓦罗兰特", "科尔维特", "特鲁姆普", "斯密麻森", "斯巴拉西", "斯国一捏",
                        "巴斯光年", "克莱斯勒", "雅诗兰黛", "马丁内斯", "玛莎拉蒂", "胡梅尔斯", "古斯塔夫",
                        "莫洛托夫", "呼伦贝尔", "齐齐哈尔", "艾斯维尔", "纳什维尔", "森海塞尔", "克伦威尔",
                        "南丁格尔", "克勒贝尔", "古铁雷斯", "劳斯莱斯", "斯台普斯", "莫比乌斯", "斯托克顿",
                        "梦比优斯", "萨博尼斯", "布达佩斯", "斯洛伐克", "拉普拉斯", "班吉拉斯", "波克基斯",
                        "拉帝欧斯", "拉帝亚斯", "双弹瓦斯", "可尔必斯", "藏马然特", "阿司匹林", "阿莫西林",
                        "俄狄浦斯", "卡利斯塔", "斯洛特金", "斯堪尼亚", "斯威士兰", "施瓦辛格",
                        "斯特拉斯堡", "罗伯斯皮尔", "斯德哥尔摩", "斯洛文尼亚", "卡萨布兰卡", "斯皮尔伯德",
                        "根特施泰纳", "威斯布鲁克", "斯塔德迈尔", "托尼克罗斯", "艾伦耶格尔", "伊斯坦布尔",
                        "戴欧奇奇斯", "泰勒巴格斯", "安东尼里弗斯", "奥斯汀里弗斯", "安东尼戴维斯",
                        "勒布朗詹姆斯", "明日方舟", "斯特罗尔"
                    ]
                    randomName = random.choice(stroll)
                    if randomName == "斯特罗尔":
                        sendMsgBody = send_group_msg(f"{randomName},真名解放！",
                                                     json_data['group_id'])
                        logger.info(f"允许 {randomName} 真名解放到 lzgz洗浴中心")
                    else:
                        msgBody = str(raw_message).replace(
                            "斯特罗尔", f"{randomName}")
                        # print(msgBody)
                        sendMsgBody = send_group_msg(msgBody,
                                                     json_data['group_id'])
                        logger.info(f"发送 {randomName} 到 lzgz洗浴中心")

                elif is_at_message(raw_message):

                    command = get_content_after_at(raw_message)
                    if command:
                        logger.info(
                            f"收到来自群组 {json_data['group_name']} ({json_data['group_id']}) 的 {json_data['sender']['nickname']} ({json_data['sender']['user_id']}) 的 at 消息: {command}"
                        )

                        if command == '6657':
                            lyb = json.loads(
                                requests.get(
                                    "https://hguofichp.cn:10086/machine/getRandOne"
                                ).text)
                            sendMsgBody = send_group_msg(
                                f"[CQ:reply,id={message_id}]{lyb['data']['barrage']}",
                                json_data['group_id'])
                            logger.info(
                                f"发送 6657 烂梗到群组 {json_data['group_id']}: {lyb['data']['barrage']}"
                            )

                        elif command == "jrrp" or command == "今日人品":
                            # 检查用户是否已同意免责声明
                            if check_user_consent(
                                    json_data['sender']['user_id']):
                                # 如果已同意，则生成并发送今日人品
                                value = get_jrrp(
                                    json_data['sender']['user_id'])
                                sendMsgBody = send_group_msg(
                                    f"[CQ:reply,id={message_id}]你今天的人品是{value}",
                                    json_data['group_id'])
                                logger.info(
                                    f"发送今日人品给 {json_data['sender']['nickname']} ({json_data['sender']['user_id']}) 到群组 {json_data['group_id']}: {value}"
                                )
                            else:
                                # 如果未同意，则发送免责声明
                                sendMsgBody = send_group_msg(
                                    f"[CQ:reply,id={message_id}]{JRRP_DISCLAIMER}",
                                    json_data['group_id'])
                                logger.info(
                                    f"向用户 {json_data['sender']['user_id']} 发送jrrp免责声明"
                                )

                        # 添加处理用户同意免责声明的命令
                        elif command == "同意jrrp免责声明":
                            # 记录用户同意
                            if add_user_consent(
                                    json_data['sender']['user_id']):
                                sendMsgBody = send_group_msg(
                                    f"[CQ:reply,id={message_id}]感谢您的理解与同意！现在您可以使用'jrrp'命令查看今日人品了。",
                                    json_data['group_id'])
                                logger.info(
                                    f"用户 {json_data['sender']['user_id']} 同意了jrrp免责声明"
                                )
                            else:
                                sendMsgBody = send_group_msg(
                                    f"[CQ:reply,id={message_id}]处理您的请求时出现错误，请稍后重试。",
                                    json_data['group_id'])
                                logger.error(
                                    f"无法记录用户 {json_data['sender']['user_id']} 的同意信息"
                                )

                        # 添加处理用户拒绝免责声明的命令
                        elif command == "拒绝jrrp免责声明":
                            # 移除用户同意记录
                            if remove_user_consent(
                                    json_data['sender']['user_id']):
                                sendMsgBody = send_group_msg(
                                    f"[CQ:reply,id={message_id}]已了解您的选择。您可以随时使用'同意jrrp免责声明'命令重新开启今日人品功能。",
                                    json_data['group_id'])
                            else:
                                sendMsgBody = send_group_msg(
                                    f"[CQ:reply,id={message_id}]处理您的请求时出现错误，请稍后重试。",
                                    json_data['group_id'])
                                logger.error(
                                    f"无法移除用户 {json_data['sender']['user_id']} 的同意信息"
                                )
                            logger.info(
                                f"用户 {json_data['sender']['user_id']} 拒绝了jrrp免责声明"
                            )

                        elif command == "给爷点赞":
                            """
                            启动主页点赞
                            """
                            requestsBody = send_like(
                                json_data['sender']['user_id'], 10)
                            logger.info(
                                f"给用户 {json_data['sender']['nickname']} ({json_data['sender']['user_id']}) 点赞10次"
                            )
                            sendMsgBody = send_group_msg(
                                f"[CQ:reply,id={message_id}]点完了喵～",
                                json_data['group_id'])
                            logger.info(
                                f"发送用户 {json_data['sender']['nickname']} ({json_data['sender']['user_id']}) 点赞完成消息到群组 {json_data['group_id']}"
                            )

                        elif command == "help":
                            """
                            发送帮助菜单
                            """
                            msgBody = f'''{BOT_NAME}菜单
🐷 6657 - 发送一条 6657 烂梗
⭐ jrrp - 今日人品
👍 给爷点赞 - 主页点赞10次
📕 help - 帮助菜单'''
                            sendMsgBody = send_group_msg(
                                f"[CQ:reply,id={message_id}]{msgBody}",
                                json_data['group_id'])
                            print(sendMsgBody)
                            logger.info(f"发送帮助信息到群组 {json_data['group_id']}")

                        else:
                            if json_data["group_id"] != 2156018119:
                                sendMsgBody = send_group_msg(
                                    f"[CQ:reply,id={message_id}]{command}",
                                    json_data['group_id'])
                                logger.info(
                                    f"发送普通消息到群组 {json_data['group_id']}: {command}"
                                )

    return {"code": "200"}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
