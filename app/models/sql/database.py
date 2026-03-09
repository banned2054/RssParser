from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app import config


class Base(DeclarativeBase) :
    """SQLAlchemy 2.0 风格的 Base 类"""
    pass


# 数据库连接配置
DATABASE_URL = f"mysql+pymysql://{config.mysql_username}:{config.REDACTED_MYSQL_PASSWORD}@{config.mysql_url}/anime"

# 创建引擎，配置连接池
engine = create_engine(
    DATABASE_URL,
    pool_recycle = 1800,
    pool_pre_ping = True,
    pool_size = 10,
    max_overflow = 20
)

# 会话工厂
Session = sessionmaker(bind = engine)


@contextmanager
def get_session() :
    """
    获取数据库会话的上下文管理器
    自动处理 commit/rollback/close
    """
    session = Session()
    try :
        yield session
        session.commit()
    except Exception :
        session.rollback()
        raise
    finally :
        session.close()


def create_all_tables() -> None :
    """创建所有定义的表（如果不存在）"""
    Base.metadata.create_all(engine)
