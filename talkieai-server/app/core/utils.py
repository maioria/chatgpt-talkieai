import hashlib
import os
import shutil
import string
import time
from datetime import datetime, timedelta
from uuid import UUID
import random

import jwt
from fastapi import UploadFile

from app.config import Config


def short_uuid() -> str:
    """64-bit characters reduced to 8-bit characters.
    link https://blog.csdn.net/dqchouyang/article/details/70230863
    """
    uuidChars = ("a", "b", "c", "d", "e", "f",
                 "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s",
                 "t", "u", "v", "w", "x", "y", "z", "0", "1", "2", "3", "4", "5",
                 "6", "7", "8", "9", "A", "B", "C", "D", "E", "F", "G", "H", "I",
                 "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V",
                 "W", "X", "Y", "Z")
    uuid = str(uuid4()).replace('-', '')
    result = ''
    for i in range(0, 8):
        sub = uuid[i * 4: i * 4 + 4]
        x = int(sub, 16)
        result += uuidChars[x % 0x3E]
    return result


def uuid4():
    """Generate a random UUID."""
    return UUID(bytes=os.urandom(16), version=4)


def digest_password(password: str):
    """Sha256 digest password"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def generate_code():
    """Generate a 4 random letter verification code"""
    code = ''.join(random.sample(string.digits, 6))
    return code


# 日期转换成 年-月-日 时:分:秒
def date_to_str(date):
    return date.strftime("%Y-%m-%d %H:%M:%S")


def day_to_str(date):
    return date.strftime("%Y-%m-%d 00:00:00")


def friendly_time(dt):
    """
    将日期时间字符串转换为友好的时间差表达方式。

    参数：
    dt -- 日期时间字符串，格式为YYYY-MM-DD HH:MM:SS

    返回值：
    友好的时间差表达方式，例如：1分钟前、1小时前、1天前等等。
    """
    now = datetime.now()
    then = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
    diff = now - then

    if diff < timedelta(seconds=60):
        return '刚刚'
    elif diff < timedelta(minutes=1):
        return f'{diff.seconds}秒前'
    elif diff < timedelta(hours=1):
        return f'{diff.seconds // 60}分钟前'
    elif diff < timedelta(days=1):
        return f'{diff.seconds // 3600}小时前'
    elif diff < timedelta(days=30):
        return f'{diff.days}天前'
    elif diff < timedelta(days=365):
        return f'{diff.days // 30}个月前'
    else:
        return f'{diff.days // 365}年前'


def save_file(upload_file: UploadFile) -> str:
    # 获取upload_file文件后缀名
    file_ext = get_file_ext(upload_file.filename)

    filename = f'{short_uuid()}{file_ext}'
    file_path = f'{Config.TEMP_SAVE_FILE_PATH}/{filename}'
    if not os.path.exists(Config.TEMP_SAVE_FILE_PATH):
        os.makedirs(Config.TEMP_SAVE_FILE_PATH)
    with open(file_path, 'wb') as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    return filename


def file_get_path(filename: str) -> str:
    return f'{Config.TEMP_SAVE_FILE_PATH}/{filename}'

# 获取文件的后缀名
def get_file_ext(filename: str) -> str:
    return os.path.splitext(filename)[1]    

# 获取年月日 yyyymmdd格式
def get_date_str():
    return time.strftime("%Y%m%d", time.localtime());