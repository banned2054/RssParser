from dataclasses import dataclass
from datetime import datetime


@dataclass
class RssItemInfo:
    item_name: str
    anime_name: str
    origin_name: str
    mikan_url: str
    bangumi_id: int
    episode: float
    pub_date: datetime
    download_finish: int
    episode_version: int
