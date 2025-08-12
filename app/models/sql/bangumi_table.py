from contextlib import contextmanager
from datetime import date
from typing import Optional

from sqlalchemy import Date, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from app import config
from app.models.bangumi_subject_info import BangumiSubjectInfo, BangumiType


# 2.0 风格的 Base
class Base(DeclarativeBase) :
    pass


# 设置 MySQL 数据库连接
DATABASE_URL = f"mysql+pymysql://{config.mysql_username}:{config.REDACTED_MYSQL_PASSWORD}@{config.mysql_url}/anime"
engine = create_engine(
        DATABASE_URL,
        pool_recycle = 1800,
        pool_pre_ping = True,
)
Session = sessionmaker(bind = engine)


@contextmanager
def get_session() :
    session = Session()
    try :
        yield session
        session.commit()
    except Exception :
        session.rollback()
        raise
    finally :
        session.close()


class BangumiInfo(Base) :
    __tablename__ = 'bangumi_info'

    bangumi_id: Mapped[int] = mapped_column(Integer, primary_key = True, nullable = False)
    platform: Mapped[str] = mapped_column(String, nullable = False)
    image_url: Mapped[str] = mapped_column(String, nullable = False)
    origin_name: Mapped[str] = mapped_column(String, nullable = False)
    cn_name: Mapped[str] = mapped_column(String, nullable = False)
    now_type: Mapped[int] = mapped_column(Integer, nullable = False)
    pubdate: Mapped[date] = mapped_column(Date, nullable = False)


class BangumiTable :
    """
    用来处理和bangumi相关的数据库的类
    """

    @staticmethod
    def create_bangumi_table_if_not_exists() :
        Base.metadata.create_all(engine)

    @staticmethod
    def insert_bangumi_data(bangumi_subject_info: BangumiSubjectInfo) :
        """
        插入一行数据
        """
        BangumiTable.create_bangumi_table_if_not_exists()
        with get_session() as session :
            new_bangumi = BangumiInfo(
                    bangumi_id = bangumi_subject_info.id,
                    platform = bangumi_subject_info.platform,
                    image_url = bangumi_subject_info.image_url,
                    origin_name = bangumi_subject_info.origin_name,
                    cn_name = bangumi_subject_info.cn_name,
                    now_type = bangumi_subject_info.now_type.value,
                    pubdate = bangumi_subject_info.pub_date
            )
            session.add(new_bangumi)

    @staticmethod
    def get_anime_info_by_id(bangumi_id: int) :
        BangumiTable.create_bangumi_table_if_not_exists()
        with get_session() as session :
            result: Optional[BangumiInfo] = session.get(BangumiInfo, bangumi_id)
            if result :
                bangumi_info = BangumiSubjectInfo(
                        id = result.bangumi_id,
                        platform = result.platform,
                        image_url = result.image_url,
                        origin_name = result.origin_name,
                        cn_name = result.cn_name,
                        now_type = BangumiType(result.now_type),
                        pub_date = result.pubdate
                )
                return True, bangumi_info
            else :
                return False, None

    @staticmethod
    def get_anime_name_by_id(bangumi_id: int) :
        BangumiTable.create_bangumi_table_if_not_exists()
        with get_session() as session :
            result = session.query(BangumiInfo).filter_by(bangumi_id = bangumi_id).first()
            if result :
                return True, result.cn_name
            else :
                return False, None

    @staticmethod
    def check_anime_exists(bangumi_id: int) :
        BangumiTable.create_bangumi_table_if_not_exists()
        with get_session() as session :
            return session.query(BangumiInfo).filter_by(bangumi_id = bangumi_id).first() is not None
