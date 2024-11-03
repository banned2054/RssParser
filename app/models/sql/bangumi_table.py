from sqlalchemy import Column, Date, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.models.bangumi_subject_info import BangumiSubjectInfo, BangumiType

Base = declarative_base()


class BangumiInfo(Base) :
    __tablename__ = 'bangumi_info'

    bangumi_id = Column(Integer, primary_key = True, nullable = False)
    platform = Column(String)
    image_url = Column(String)
    origin_name = Column(String)
    cn_name = Column(String)
    now_type = Column(Integer)
    pubdate = Column(Date)


DATABASE_URL = 'sqlite:///data/anime.db'
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind = engine)


class BangumiTable :
    """
    用来处理和bangumi相关的数据库的类
    """

    @staticmethod
    def create_bangumi_table_if_not_exists() :
        Base.metadata.create_all(engine)

    @staticmethod
    def insert_bangumi_data(
            bangumi_subject_info: BangumiSubjectInfo) :
        """
        插入一行数据
        """
        BangumiTable.create_bangumi_table_if_not_exists()
        session = Session()
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
        session.commit()
        session.close()

    @staticmethod
    def get_anime_info_by_id(bangumi_id: int) :
        BangumiTable.create_bangumi_table_if_not_exists()
        session = Session()
        result = session.query(BangumiInfo).filter_by(bangumi_id = bangumi_id).first()
        session.close()
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
        session = Session()
        result = session.query(BangumiInfo).filter_by(bangumi_id = bangumi_id).first()
        session.close()
        if result :
            cn_name = result.cn_name
            return True, cn_name
        else :
            return False, None

    @staticmethod
    def check_anime_exists(bangumi_id: int) :
        BangumiTable.create_bangumi_table_if_not_exists()
        session = Session()
        exists = session.query(BangumiInfo).filter_by(bangumi_id = bangumi_id).first() is not None
        session.close()
        return exists
