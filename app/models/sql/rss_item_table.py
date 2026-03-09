from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, Integer, String, select
from sqlalchemy.orm import Mapped, mapped_column

from app.models.mikan_rss_info import RssItemInfo
from app.models.sql.database import Base, engine, get_session
from app.utils.log_utils import set_up_logger

logger = set_up_logger(__name__)


class RssItem(Base) :
    __tablename__ = 'rss_item'

    # 主键
    mikan_url: Mapped[str] = mapped_column(String, primary_key = True, nullable = False)

    item_name: Mapped[str] = mapped_column(String, nullable = False)
    anime_name: Mapped[str] = mapped_column(String, nullable = False)
    origin_name: Mapped[str] = mapped_column(String, nullable = False)
    torrent_hash: Mapped[str] = mapped_column(String, nullable = False)
    bangumi_id: Mapped[int] = mapped_column(Integer, nullable = False)
    episode: Mapped[float] = mapped_column(Float, nullable = False)
    pub_date: Mapped[datetime] = mapped_column(DateTime, nullable = False)
    download_finish: Mapped[bool] = mapped_column(Boolean, nullable = False, default = False)
    version: Mapped[int] = mapped_column(Integer, nullable = False, default = 0)


# 模块加载时创建表
Base.metadata.create_all(engine)


class RssItemTable :
    """
    用来处理和rss相关的数据库的类
    """

    @staticmethod
    def insert_rss_data(item_info: RssItemInfo, hash_code: str, download_finish: bool = False) -> None :
        with get_session() as session :
            # 若上游给的是 ISO 字符串，这里转换成 datetime
            pub_date = item_info.pub_date
            if isinstance(pub_date, str) :
                pub_date = datetime.fromisoformat(pub_date)

            new_item = RssItem(
                item_name = item_info.item_name,
                anime_name = item_info.anime_name,
                origin_name = item_info.origin_name,
                mikan_url = item_info.mikan_url,
                torrent_hash = hash_code,
                bangumi_id = item_info.bangumi_id,
                episode = item_info.episode,
                pub_date = pub_date,
                download_finish = download_finish,
                version = item_info.episode_version,
            )
            session.add(new_item)

    @staticmethod
    def check_item_exist(mikan_url: str) -> bool :
        # 主键查询用 get 最简洁，类型也最友好
        with get_session() as session :
            return session.get(RssItem, mikan_url) is not None

    @staticmethod
    def get_bangumi_id_by_anime_name(anime_name: str) -> int :
        with get_session() as session :
            stmt = select(RssItem.bangumi_id).where(RssItem.anime_name == anime_name).distinct()
            bangumi_id: Optional[int] = session.execute(stmt).scalars().first()
            return bangumi_id if bangumi_id is not None else -1

    @staticmethod
    def get_not_finished_download_item() -> list[str] :
        with get_session() as session :
            stmt = select(RssItem.torrent_hash).where(RssItem.download_finish.is_(False))
            return list(session.execute(stmt).scalars().all())

    @staticmethod
    def finish_item_download(hash_code: str) -> None :
        with get_session() as session :
            stmt = select(RssItem).where(RssItem.torrent_hash == hash_code)
            item: Optional[RssItem] = session.execute(stmt).scalars().first()
            if item :
                item.download_finish = True  # flush/commit 在 contextmanager 里处理

    @staticmethod
    def get_item_info_by_hash(hash_code: str) -> tuple[bool, Optional[RssItemInfo]] :
        with get_session() as session :
            stmt = select(RssItem).where(RssItem.torrent_hash == hash_code)
            item: Optional[RssItem] = session.execute(stmt).scalars().first()
            if not item :
                return False, None
            return True, RssItemInfo(
                item_name = item.item_name,
                anime_name = item.anime_name,
                origin_name = item.origin_name,
                mikan_url = item.mikan_url,
                bangumi_id = item.bangumi_id,
                episode = item.episode,
                pub_date = item.pub_date,
                download_finish = item.download_finish,
                episode_version = item.version
            )

    @staticmethod
    def get_latest_episode_torrent(bangumi_id: int, episode: float) -> Optional[RssItemInfo] :
        with get_session() as session :
            stmt = (
                    select(RssItem)
                    .where(RssItem.bangumi_id == bangumi_id, RssItem.episode == episode)
                    .order_by(RssItem.pub_date.desc())
                    .limit(1)
            )
            item: Optional[RssItem] = session.execute(stmt).scalars().first()
            if not item :
                return None

            return RssItemInfo(
                item_name = item.item_name,
                anime_name = item.anime_name,
                origin_name = item.origin_name,
                mikan_url = item.mikan_url,
                bangumi_id = item.bangumi_id,
                episode = item.episode,
                pub_date = item.pub_date,
                download_finish = item.download_finish,
                episode_version = item.version,
            )

    @staticmethod
    def get_episode_hashes(bangumi_id: int, episode: float) -> list[str] :
        with get_session() as session :
            stmt = select(RssItem.torrent_hash).where(
                RssItem.bangumi_id == bangumi_id,
                RssItem.episode == episode,
            )
            return list(session.execute(stmt).scalars().all())
