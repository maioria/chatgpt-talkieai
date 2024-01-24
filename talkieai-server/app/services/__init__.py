from app.services.sys_service import SysService
from app.services.account_service import AccountService
from app.services.chat_service import ChatService
from app.services.topic_service import TopicService
from app.db import SessionLocal



# 检查初始化数据
db = SessionLocal()
sys_service = SysService(db)
account_service = AccountService(db)
topic_service = TopicService(db)
chat_service = ChatService(db)
db.close()