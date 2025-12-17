import hashlib
import hmac
from datetime import datetime
import math
import sqlite3
import os

"""

今日人品计算

"""

def get_jrrp(qid):
    """
    根据QQ号码生成当天的0-100固定值（增强版算法）

    Args:
        qid: 字符串或整数形式的QQ号码

    Returns:
        int: 当天的0-100之间的固定值
    """
    # 获取当前日期相关信息
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    year = now.year
    month = now.month
    day = now.day

    # 步骤1: 创建基础组合字符串
    base_str = f"{qid}_{today_str}_{year}_{month}_{day}"

    # 步骤2: 生成主盐值（使用多层哈希）
    salt1 = hashlib.sha3_256(f"salt_{qid}_{year}".encode()).hexdigest()
    salt2 = hashlib.sha512(f"pepper_{today_str}_{month}".encode()).hexdigest()
    combined_salt = hmac.new(salt1.encode(), salt2.encode(),
                             hashlib.blake2b).hexdigest()

    # 步骤3: 第一次哈希计算（带盐）
    first_hash = hashlib.pbkdf2_hmac(
        "sha256",
        base_str.encode(),
        combined_salt.encode(),
        1000  # 迭代次数
    ).hex()

    # 步骤4: 第二次哈希计算（混合算法）
    # 将第一次哈希结果分为两部分
    mid_point = len(first_hash) // 2
    part1 = first_hash[:mid_point]
    part2 = first_hash[mid_point:]

    # 使用不同的哈希算法处理两部分
    hash_part1 = hashlib.sha224(part1.encode()).hexdigest()
    hash_part2 = hashlib.sha384(part2.encode()).hexdigest()

    # 合并结果
    second_hash = hash_part1 + hash_part2

    # 步骤5: 数学变换增强随机性
    hash_int = int(second_hash, 16)

    # 添加数学变换：使用正弦函数增加非线性
    sin_value = abs(math.sin(hash_int))
    transformed = int(hash_int * sin_value)

    # 步骤6: 映射到0-100范围
    # 使用双重取模增加分布均匀性
    step1 = transformed % 1000001
    jrrp = step1 % 101

    return jrrp

"""

用户协议记录

"""

DB_FILE = "jrrpUserConsent.db"

def init_database():
    """
    初始化数据库，创建用户同意记录表
    """
    # 检查数据库文件是否存在，不存在则创建
    db_exists = os.path.exists(DB_FILE)

    # 连接数据库
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # 创建用户同意记录表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_consent (
        user_id INTEGER PRIMARY KEY,
        consent_time TEXT NOT NULL,
        consent_version TEXT NOT NULL
    )
    ''')

    # 提交事务并关闭连接
    conn.commit()
    conn.close()

    # 如果是新创建的数据库，记录日志
    if not db_exists:
        print(f"数据库 {DB_FILE} 已创建并初始化")


def check_user_consent(user_id):
    """
    检查用户是否已同意免责声明
    
    Args:
        user_id: 用户的QQ号码
        
    Returns:
        bool: 如果用户已同意则返回True，否则返回False
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # 查询用户是否已同意
        cursor.execute("SELECT 1 FROM user_consent WHERE user_id = ?",
                       (user_id, ))
        result = cursor.fetchone()

        conn.close()

        # 如果有记录，则用户已同意
        return result is not None
    except Exception as e:
        print(f"检查用户同意状态时出错: {e}")
        return False


def add_user_consent(user_id, consent_version="1.0"):
    """
    添加用户同意记录
    
    Args:
        user_id: 用户的QQ号码
        consent_version: 同意的免责声明版本号
        
    Returns:
        bool: 操作是否成功
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # 获取当前时间
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 检查用户是否已存在
        cursor.execute("SELECT 1 FROM user_consent WHERE user_id = ?",
                       (user_id, ))
        exists = cursor.fetchone()

        if exists:
            # 更新现有记录
            cursor.execute(
                "UPDATE user_consent SET consent_time = ?, consent_version = ? WHERE user_id = ?",
                (now, consent_version, user_id))
        else:
            # 添加新记录
            cursor.execute(
                "INSERT INTO user_consent (user_id, consent_time, consent_version) VALUES (?, ?, ?)",
                (user_id, now, consent_version))

        conn.commit()
        conn.close()

        return True
    except Exception as e:
        print(f"添加用户同意记录时出错: {e}")
        conn.rollback()
        conn.close()
        return False


def remove_user_consent(user_id):
    """
    移除用户同意记录
    
    Args:
        user_id: 用户的QQ号码
        
    Returns:
        bool: 操作是否成功
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM user_consent WHERE user_id = ?",
                       (user_id, ))
        conn.commit()
        conn.close()

        return True
    except Exception as e:
        print(f"移除用户同意记录时出错: {e}")
        conn.rollback()
        conn.close()
        return False


# 在模块加载时自动初始化数据库
init_database()

