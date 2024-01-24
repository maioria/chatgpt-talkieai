import json
from app.core.logging import logging

language_data = []

azure_data = {}
with open("data/azure.json", "r") as f:
    azure_data = json.load(f)

azure_style_label_data = []
with open("data/azure_style_label.json", "r") as f:
    azure_style_label_data = json.load(f) 

azure_style_label_map = {}
for item in azure_style_label_data:
    azure_style_label_map[item["value"]] = item["label"]   

sys_language_data = {}
with open("data/sys_language.json", "r") as f:
    sys_language_data = json.load(f)

def get_label_by_language(language: str) -> str:
    """根据语言获取对应的label"""
    for item in sys_language_data:
        if item["value"] == language:
            return item["label"]
    raise Exception("没有找到对应的语言:{language}")

def get_azure_style_label(style: str):
    """根据style获取对应的label"""
    # 检查azure_style_label_map是否包含style
    if style in azure_style_label_map:
        return azure_style_label_map[style]
    logging.warning(f"没有找到对应的style:{style}")
    return ""

def get_azure_language_default_role(language: str):
    """根据语言获取默认的角色"""
    for item in sys_language_data:
        if item["value"] == language:
            return item["default_voice_role_name"]
    raise Exception(f"没有找到对应的语言:{language}")

def get_role_info_by_short_name(short_name: str):
    """根据short_name获取角色信息"""
    for item in sys_language_data:
        if item["short_name"] == short_name:
            return item
    raise Exception(f"没有找到对应的角色:{short_name}")

