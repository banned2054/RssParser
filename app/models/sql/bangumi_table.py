from datetime import date
from typing import Optional

from sqlalchemy import Date, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.bangumi_subject_info import BangumiSubjectInfo, BangumiType
from app.models.sql.database import Base, create_all_tables, get_session


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
    def create_bangumi_table_if_not_exists() -> None :
        create_all_tables()

    @staticmethod
    def insert_bangumi_data(bangumi_subject_info: BangumiSubjectInfo) -> None :
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
    def get_anime_info_by_id(bangumi_id: int) -> tuple[bool, Optional[BangumiSubjectInfo]] :
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
    def get_anime_name_by_id(bangumi_id: int) -> tuple[bool, Optional[str]] :
        BangumiTable.create_bangumi_table_if_not_exists()
        with get_session() as session :
            result = session.query(BangumiInfo).filter_by(bangumi_id = bangumi_id).first()
            if result :
                return True, result.cn_name
            else :
                return False, None

    @staticmethod
    def check_anime_exists(bangumi_id: int) -> bool :
        BangumiTable.create_bangumi_table_if_not_exists()
        with get_session() as session :
            return session.query(BangumiInfo).filter_by(bangumi_id = bangumi_id).first() is not None
