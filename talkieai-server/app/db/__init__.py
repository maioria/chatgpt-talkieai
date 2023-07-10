from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import Config
from sqlalchemy.exc import DisconnectionError


def checkout_listener(dbapi_con, con_record, con_proxy):
    try:
        try:
            dbapi_con.ping(False)
        except TypeError:
            dbapi_con.ping()
    except dbapi_con.OperationalError as exc:
        if exc.args[0] in (2006, 2013, 2014, 2045, 2055):
            raise DisconnectionError()
        else:
            raise


# 创建数据库连接, SQLALCHEMY_DATABASE_URL不能为空
if not Config.SQLALCHEMY_DATABASE_URL:
    raise Exception('SQLALCHEMY_DATABASE_URL不能为空')
engine = create_engine(Config.SQLALCHEMY_DATABASE_URL, echo=Config.SQL_ECHO, pool_pre_ping=True, pool_size=100, pool_recycle=360)
event.listen(engine, 'checkout', checkout_listener)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()


# 数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
