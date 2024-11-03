import datetime
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.models.mikan_rss_info import RssItemInfo

Base = declarative_base()


class RssItem(Base) :
    __tablename__ = 'rss_item'

    item_name = Column(String)
    anime_name = Column(String)
    origin_name = Column(String)
    mikan_url = Column(String, primary_key = True)
    torrent_hash = Column(String)
    bangumi_id = Column(Integer)
    episode = Column(Float)
    pub_date = Column(DateTime)
    download_finish = Column(Boolean, default = False)
    version = Column(Integer)  # 添加的新列


DATABASE_URL = 'sqlite:///data/rss.db'
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind = engine)
Base.metadata.create_all(engine)


class RssItemTable :
    """
    用来处理和rss相关的数据库的类
    """

    @staticmethod
    def insert_rss_data(item_info, hash_code, download_finish = False) :
        session = Session()

        # 确保pub_date是datetime对象
        if isinstance(item_info.pub_date, str) :
            item_info.pub_date = datetime.fromisoformat(item_info.pub_date)

        new_item = RssItem(
                item_name = item_info.item_name,
                anime_name = item_info.anime_name,
                origin_name = item_info.origin_name,
                mikan_url = item_info.mikan_url,
                torrent_hash = hash_code,
                bangumi_id = item_info.bangumi_id,
                episode = item_info.episode,
                pub_date = item_info.pub_date,
                download_finish = download_finish,
                version = item_info.episode_version  # 添加的新列
        )
        session.add(new_item)
        session.commit()
        session.close()

    @staticmethod
    def check_item_exist(mikan_url) :
        session = Session()
        exists = session.query(RssItem).filter(RssItem.mikan_url == mikan_url).count() > 0
        session.close()
        return exists

    @staticmethod
    def get_bangumi_id_by_anime_name(anime_name) :
        session = Session()
        result = session.query(RssItem.bangumi_id).filter(RssItem.anime_name == anime_name).distinct().first()
        session.close()
        return result.bangumi_id if result else -1

    @staticmethod
    def get_not_finished_download_item() :
        session = Session()
        unfinished_downloads = [item.torrent_hash for item in
                                session.query(RssItem).filter(RssItem.download_finish == False).all()]
        session.close()
        return unfinished_downloads

    @staticmethod
    def finish_item_download(hash_code) :
        session = Session()
        item = session.query(RssItem).filter(RssItem.torrent_hash == hash_code).first()
        if item :
            item.download_finish = True
            session.commit()
        session.close()

    @staticmethod
    def get_item_info_by_hash(hash_code) :
        session = Session()
        item = session.query(RssItem).filter(RssItem.torrent_hash == hash_code).first()
        if item :
            item_info = RssItemInfo(
                    item_name = item.item_name,
                    anime_name = item.anime_name,
                    origin_name = item.origin_name,
                    mikan_url = item.mikan_url,
                    bangumi_id = item.bangumi_id,
                    episode = item.episode,
                    pub_date = item.pub_date,
                    download_finish = item.download_finish,
                    episode_version = item.version  # 添加的新列
            )
            session.close()
            return True, item_info
        else :
            session.close()
            return False, None

    @staticmethod
    def get_latest_episode_torrent(bangumi_id: int, episode: float) :
        session = Session()
        item = session.query(RssItem).filter(RssItem.bangumi_id == bangumi_id, RssItem.episode == episode).order_by(
                RssItem.pub_date.desc()).first()
        if item :
            item_info = RssItemInfo(
                    item_name = item.item_name,
                    anime_name = item.anime_name,
                    origin_name = item.origin_name,
                    mikan_url = item.mikan_url,
                    bangumi_id = item.bangumi_id,
                    episode = item.episode,
                    pub_date = item.pub_date,
                    download_finish = item.download_finish,
                    episode_version = item.version  # 添加的新列
            )
            session.close()
            return item_info
        else :
            session.close()
            return None
