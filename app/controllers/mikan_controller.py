import traceback
from typing import Tuple

import feedparser
from pyaniparser import AniParser
from pyaniparser.types import EnumLanguage, EnumMediaType, EnumResolution, ParseResult

from app import config
from app.models.mikan_rss_info import RssItemInfo
from app.models.sql import BangumiTable, RssItemTable
from app.utils.log_utils import set_up_logger
from app.utils.net_utils import download_file, fetch_xml
from app.utils.parser.bangumi_parser import get_subject_info
from app.utils.parser.mikan_parser import get_anime_home_url_from_mikan, get_bangumi_url_from_mikan
from app.utils.parser.title_parser import clear_title, universal_replace_name
from app.utils.time_utils import datetime_to_str, struct_time_to_datetime
from app.utils.torrent.qbittorrent_utils import delete_torrent_by_hash, download_one_file

logger = set_up_logger(__name__)

ani = AniParser()


async def fresh_rss() :
    try :
        config.fresh_config()
        rss_url = config.rss_url
        if not rss_url :
            raise Exception("rss link is empty")

        ok, data = await fetch_xml(rss_url)
        if not ok :
            raise Exception(f"fetch rss failed: {data}")
        logger.info(f"fetch mikan rss")
        feed = feedparser.parse(data)
        if getattr(feed, "bozo", 0) :
            err = getattr(feed, "bozo_exception", None)
            raise Exception(f"parse rss failed: {err!r}")

        for item in reversed(getattr(feed, "entries", [])) :
            await analyze_item(item)
        return True, "ok"
    except Exception as e :
        handle_exception(e)
        return False, str(e)


def handle_exception(e) :
    # 兼容原签名，但更稳健
    try :
        error_str = str(e)
        tb = traceback.extract_tb(e.__traceback__) if e.__traceback__ else []
        filename = tb[-1].filename if tb else "<unknown>"
        lineno = tb[-1].lineno if tb else -1
        logger.error(
            f"Try to fresh rss failed: {error_str}; file name: {filename}, line: {lineno}"
        )
    finally :
        logger.error("Exception occurred")


async def analyze_item(item) :
    parseResult = ani.parse(item.title)
    if parseResult is None :
        return
    should_skip, now_language = should_skip_item(parseResult)
    if should_skip :
        return
    title = parseResult.title
    mikan_url = item["link"].split(config.mikan_episode)[-1]

    if RssItemTable.check_item_exist(mikan_url) :
        return

    logger.info(f"add new torrent: {clear_title(item.title)}")

    if parseResult.media_type is EnumMediaType.MultipleEpisode :
        episode = parseResult.start_episode
        version = 1
    else :
        episode = parseResult.episode
        version = parseResult.version

    bangumi_subject_id = RssItemTable.get_bangumi_id_by_anime_name(title)
    bangumi_subject_id, episode = _apply_subject_fixes(bangumi_subject_id, episode)
    if bangumi_subject_id == -1 :
        bangumi_subject_id = await get_bangumi_url(item)
        if bangumi_subject_id == -1 :
            return
        anime_info, item_info = await process_new_bangumi_item(
            item, bangumi_subject_id, episode, title, item.title, mikan_url, version)
    else :
        anime_info, item_info = await process_existing_bangumi_item(
            item, bangumi_subject_id, episode, title, item.title, mikan_url, version)

    latest = RssItemTable.get_latest_episode_torrent(anime_info.id, episode)
    if now_language == 'baha' and latest is not None :
        return

    hash_list = RssItemTable.get_episode_hashes(anime_info.id, episode)
    ok, torrent_path = await download_mikan_torrent(item)
    if not ok :
        return

    for now_hash in hash_list :
        RssItemTable.finish_item_download(now_hash)
        delete_torrent_by_hash(now_hash)

    await download_and_notify(torrent_path, anime_info, item_info, now_language)


def should_skip_item(result: ParseResult) :
    if result is None :
        return True, None
    if result.resolution is not EnumResolution.R1080p :
        return True, None
    if result.group.lower() == 'ani' :
        return False, "baha"
    if result.group.lower() == 'lolihouse' :
        return False, "LoliHouse"
    if result.language is EnumLanguage.JpSc or result.language is EnumLanguage.Sc :
        return False, "Sc"
    return True, None


async def get_bangumi_url(item) :
    mikan_url = item["link"].split(config.mikan_episode)[-1]

    mikan_home_url = await get_anime_home_url_from_mikan(mikan_url)
    if not mikan_home_url[0] :
        return -1
    bangumi_url = await get_bangumi_url_from_mikan(mikan_home_url[1])
    if not bangumi_url[0] :
        return -1
    try :
        subject_id = int(str(bangumi_url[1]).split("https://bgm.tv/subject/")[-1])
    except Exception :
        logger.error(f"parse subject id failed from url: {bangumi_url[1]}")
        return -1
    return subject_id


async def process_new_bangumi_item(item, subject_id, episode, origin_title, item_title, torrent_page_url, version) :
    anime_info = get_subject_info(subject_id)
    if anime_info is None :
        return None, None

    item_name = universal_replace_name("file_name", anime_info, episode)
    pub_date = datetime_to_str(struct_time_to_datetime(item["published_parsed"]))
    item_info = RssItemInfo(item_name, origin_title, item_title, torrent_page_url, subject_id, episode, pub_date, 0,
                            version)

    if not BangumiTable.check_anime_exists(subject_id) :
        BangumiTable.insert_bangumi_data(anime_info)
    return anime_info, item_info


async def process_existing_bangumi_item(item, subject_id, episode, origin_title, item_title, torrent_page_url,
                                        version) :
    anime_info = BangumiTable.get_anime_info_by_id(subject_id)
    if not anime_info[0] :
        return None, None

    item_name = universal_replace_name("file_name", anime_info[1], episode)
    pub_date = datetime_to_str(struct_time_to_datetime(item["published_parsed"]))
    item_info = RssItemInfo(item_name, origin_title, item_title, torrent_page_url, subject_id, episode, pub_date, 0,
                            version)

    return anime_info[1], item_info


async def download_and_notify(torrent_path, anime_info, item_info, now_language) :
    save_path = determine_save_path(anime_info)
    dir_name = universal_replace_name("dir_name", anime_info)
    file_name = universal_replace_name("file_name", anime_info, item_info.episode)
    new_torrent_name = universal_replace_name("qbittorrent_name", anime_info, item_info.episode)
    if now_language == 'baha' :
        new_torrent_name += ' BAHA'
    else :
        new_torrent_name += ' Mikan'

    await download_one_file(torrent_path, new_torrent_name, save_path, dir_name, file_name, "mikan", item_info)


def determine_save_path(anime_info) :
    base = config.get_config("download_path")
    anime_path = config.get_config("anime_path")
    toku_path = config.get_config("tokusatsu_path")
    if getattr(anime_info.now_type, "value", None) == 2 :
        return f"{base}/{anime_path}"
    else :
        return f"{base}/{toku_path}"


async def download_mikan_torrent(item) :
    try :
        for enclosure in getattr(item, "enclosures", []) :
            if enclosure.get("type") != "application/x-bittorrent" :
                continue
            torrent_url = enclosure.get("href")
            if not torrent_url :
                continue

            resp = await download_file(torrent_url, "download")
            if not resp[0] :
                logger.error(f"下载torrent文件失败: {resp[1]}")
                return False, resp[1]
            torrent_path = resp[1]
            logger.info(f"下载torrent文件, 路径:{torrent_path}")
            return True, torrent_path
        return False, "没有torrent链接"
    except Exception as e :
        handle_exception(e)
        return False, str(e)


def _apply_subject_fixes(subject_id: int, episode: int) -> Tuple[int, int] :
    """
    特例修正集中管理：
    - (ep>24 且 420628) -> 486347
    - (ep>12 且 467461) -> 529431
    - (id==484623 且 ep>13) -> ep-=13
    """
    replace_rules = (
            (24, 420628, 486347),
            (12, 467461, 529431),
    )
    for ep_th, old_id, new_id in replace_rules :
        if episode > ep_th and subject_id == old_id :
            subject_id = new_id
            break

    if episode > 13 and subject_id == 484623 :
        episode -= 13

    return subject_id, episode
