import json
import os
from pydub import AudioSegment
from sqlalchemy.orm import Session
from app.core.utils import *
from app.core.exceptions import *
from app.core.utils import *
from app.db.account_entities import *
from app.db.sys_entities import *
from app.core.logging import logging
from app.models.sys_models import *
from app.core.language import *

# 读取data下 language_demo_map.json 生成对应字典
LANGUAGE_DICT_KEY = "learn_language"
language_demo_map = {}
with open("data/language_demo_map.json", "r") as f:
    language_demo_map = json.load(f)


class SysService:
    def __init__(self, db: Session):
        self.db = db
        # 查出所有系统配置的语言，并且生成默认角色与语气的信息
        self._check_and_init_default_learn_languages()

    def get_settings_roles(self, locale: str, account_id: str):
        """根据语言获取语言下所有支持的角色"""
        roles = (
            self.db.query(SettingsRoleEntity)
            .filter_by(locale=locale, deleted=0)
            .order_by(SettingsRoleEntity.name.asc())
            .all()
        )

        result = []
        for role in roles:
            # 通过roles批量获取所有的style，并且在迭代中进行组装
            styles = json.loads(role.styles)
            # 转换成value、label格式
            styles_data = []
            for style in styles:
                if style:
                    styles_data.append(
                        {"value": style, "label": get_azure_style_label(style)}
                    )
                else:
                    styles_data.append({"value": "", "label": ""})
            result.append(
                {
                    "id": role.id,
                    "name": role.name,
                    "locale": role.locale,
                    "local_name": role.local_name,
                    "short_name": role.short_name,
                    "avatar": role.avatar,
                    "audio": role.audio,
                    "speech_content": "",
                    "gender": role.gender,
                    "styles": styles_data,
                }
            )
        return result

    def get_settings_languages_example(self, language: str, account_id: str):
        """获取语言下的示例"""
        # 获取语言下的示例
        # 语言没有国家  所以去掉后面的国家后缀
        language = language.split("-")[0]
        languages = (
            self.db.query(SettingsLanguageExampleEntity)
            .filter_by(language=language)
            .first()
        )
        return languages.example

    def get_settings_languages(self, account_id: str):
        """获取用户支持的所有语种"""
        # sys_dict_data 获取  dict_type 为 learn_language 的数据
        sys_dict_data_entities = (
            self.db.query(SysDictDataEntity)
            .filter(SysDictDataEntity.dict_type == LANGUAGE_DICT_KEY)
            .all()
        )
        # 取出dict_label 与 dict_value 返回
        result = []
        for sys_dict_data_entity in sys_dict_data_entities:
            result.append(
                {
                    "label": sys_dict_data_entity.dict_label,
                    "value": sys_dict_data_entity.dict_value,
                }
            )
        return result

    def get_settings_languages_example(self, language: str, account_id: str):
        """获取语言下的示例"""
        # 获取语言下的示例
        # 语言没有国家  所以去掉后面的国家后缀
        language = language.split("-")[0]
        return language_demo_map[language]

    def voice_upload(self, file: UploadFile, account_id: str):
        """用户上传语音文件"""
        file_name = save_voice_file(file, account_id)
        # 如果上传的是mp3格式(暂时只有android手机只能用mp3格式), 就转换成wav返回, 为了后续azure服务解析音频(mp3会解析失败), 因为chat接口本身比较慢，所以在这里进行转换
        if file.filename.endswith(".mp3"):
            mp3_file_path = file_get_path(file_name)
            wav_file_name = file_name.replace(".mp3", ".wav")
            wav_file_path = file_get_path(wav_file_name)
            sound = AudioSegment.from_mp3(mp3_file_path)
            sound.export(wav_file_path, format="wav")
            # mp3文件需要删除
            os.remove(mp3_file_path)
            file_name = wav_file_name
        return {"file": file_name}

    def add_feedback(self, dto: FeedbackDTO, account_id: str):
        add_feedback = FeedbackEntity(
            account_id=account_id, content=dto.content, contact=dto.contact
        )
        self.db.add(add_feedback)
        self.db.commit()
        self.db.refresh(add_feedback)

    def _check_and_init_default_learn_languages(self):
        # 查出所有系统配置的语言
        sys_dict_data_entities = (
            self.db.query(SysDictDataEntity)
            .filter(SysDictDataEntity.dict_type == LANGUAGE_DICT_KEY)
            .all()
        )
        # sys_dict_data_entities 为空的话加载默认的语言
        if sys_dict_data_entities:
            return

        # 加载 data下 sys_language.json文件，生成初始值
        with open("data/sys_language.json", "r") as f:
            sys_language = json.load(f)
        # 保存到数据库中
        for language in sys_language:
            add_language = SysDictDataEntity(
                dict_type=LANGUAGE_DICT_KEY,
                dict_label=language["label"],
                dict_value=language["value"],
            )
            self.db.add(add_language)
            # 继续检查角色的配置
            self._check_and_init_default_roles(add_language.dict_value)
        self.db.commit()

    def _check_and_init_default_roles(self, locale: str):
        """检查是否初始化了数据，如果未初始化，从azure获取所有的角色，并且保存到数据库中"""
        # 查出所有系统配置的角色
        roles = (
            self.db.query(SettingsRoleEntity).filter_by(locale=locale, deleted=0).all()
        )
        if roles:
            return
        
        roles = [role for role in azure_data if role["locale"] == locale]
        # 保存到数据库中
        for role in roles:
            add_role = SettingsRoleEntity(
                name=role["name"],
                locale=role["locale"],
                local_name=role["local_name"],
                short_name=role["short_name"],
                gender=role["gender"],
                styles=json.dumps(role["style_list"]),
            )
            self.db.add(add_role)

        self.db.commit()
