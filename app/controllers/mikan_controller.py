import traceback

import feedparser

from app import config
from app.models.mikan_rss_info import RssItemInfo
from app.models.sql import BangumiTable, RssItemTable
from app.utils.log_utils import set_up_logger
from app.utils.net_utils import download_file, fetch
from app.utils.parser.bangumi_parser import get_subject_info
from app.utils.parser.mikan_parser import get_anime_home_url_from_mikan, get_bangumi_url_from_mikan
from app.utils.parser.title_parser import get_episode, get_subtitle_language, get_title, \
    universal_replace_name
from app.utils.time_utils import datetime_to_str, struct_time_to_datetime
from app.utils.torrent.qbittorrent_utils import download_one_file

logger = set_up_logger(__name__)


async def fresh_rss() :
    try :
        config.fresh_config()
        rss_url = config.rss_url
        if rss_url == "" :
            raise Exception("rss link is empty")

        # 访问rss链接，并解析
        rss_page = await fetch(rss_url)
        logger.info("fetch rss")
        feed = feedparser.parse(rss_page[1])

        # 查询每一个item
        for item in reversed(feed.entries) :
            await analyze_item(item)
    except Exception as e :
        handle_exception(e)
        return False, str(e)


def handle_exception(e) :
    error_str = str(e)
    tb = traceback.extract_tb(e.__traceback__)
    filename = tb[-1].filename
    lineno = tb[-1].lineno
    logger.error(
            f"Try to fresh rss failed: {error_str}; file name: {filename}, line: {lineno}"
    )


def contains_any(main_str, str_list) :
    for sub_str in str_list :
        if sub_str in main_str :
            return True
    return False


async def analyze_item(item) :
    item_title = item.title
    should_skip, now_language = should_skip_item(item_title)
    if should_skip :
        return

    origin_title = get_title(item_title)
    if origin_title == "" :
        return

    mikan_url = item["link"].split(config.mikan_episode)[-1]

    if RssItemTable.check_item_exist(mikan_url) :
        return

    bangumi_subject_id = RssItemTable.get_bangumi_id_by_anime_name(origin_title)
    logger.info(f"add new torrent: {item.title}")
    origin_title = get_title(item_title)
    episode1, version1, episode2, version2 = get_episode(item_title)

    if bangumi_subject_id == -1 :
        bangumi_subject_id = await get_bangumi_url(item)
        if bangumi_subject_id == -1 :
            return
        anime_info, item_info = await process_new_bangumi_item(item,
                                                               bangumi_subject_id,
                                                               episode1,
                                                               origin_title,
                                                               item_title,
                                                               mikan_url, version1)
    else :
        anime_info, item_info = await process_existing_bangumi_item(item, item_title, mikan_url, bangumi_subject_id)

    latest = RssItemTable.get_latest_episode_torrent(anime_info.id, episode1)
    if now_language == 'baha' and latest is not None :
        return

    torrent_result = await download_mikan_torrent(item)
    if not torrent_result[0] :
        return
    await download_and_notify(torrent_result[1], anime_info, item_info, now_language)


def should_skip_item(item_title) :
    """
    判断是否有filter的内容、以及语言是否正确
    """
    if contains_any(item_title, config.filters) :
        return True, None

    now_language = get_subtitle_language(item_title)
    target_language = config.get_config("subtitle_language")

    if now_language == 'baha' :
        return False, 'baha'

    if now_language != target_language :
        return True, None

    return False, now_language


async def get_bangumi_url(item) :
    mikan_url = item["link"].split(config.mikan_episode)[-1]

    mikan_home_url = await get_anime_home_url_from_mikan(mikan_url)
    if not mikan_home_url[0] :
        return -1
    bangumi_url = await get_bangumi_url_from_mikan(mikan_home_url[1])
    if not bangumi_url[0] :
        return -1
    subject_id = int(bangumi_url[1].split("https://bgm.tv/subject/")[-1])
    return subject_id


async def process_new_bangumi_item(item, subject_id, episode, origin_title, item_title, torrent_page_url, version) :
    anime_info = get_subject_info(subject_id)
    if anime_info is None :
        return

    item_name = universal_replace_name("file_name", anime_info, episode)
    pub_date = datetime_to_str(struct_time_to_datetime(item["published_parsed"]))
    item_info = RssItemInfo(item_name, origin_title, item_title, torrent_page_url, subject_id, episode, pub_date, 0,
                            version)

    if not BangumiTable.check_anime_exists(subject_id) :
        BangumiTable.insert_bangumi_data(anime_info)
    return anime_info, item_info


async def process_existing_bangumi_item(item, item_title, torrent_page_url, bangumi_id) :
    origin_title = get_title(item_title)
    episode1, version1, episode2, version2 = get_episode(item_title)
    anime_info = BangumiTable.get_anime_info_by_id(bangumi_id)
    if not anime_info[0] :
        return

    item_name = universal_replace_name("file_name", anime_info[1], episode1)
    pub_date = datetime_to_str(struct_time_to_datetime(item["published_parsed"]))
    item_info = RssItemInfo(item_name, origin_title, item_title, torrent_page_url, bangumi_id, episode1, pub_date, 0,
                            version1)

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
    if anime_info.now_type.value == 2 :
        return f"{config.get_config('download_path')}/{config.get_config('anime_path')}"
    else :
        return f"{config.get_config('download_path')}/{config.get_config('tokusatsu_path')}"


async def download_mikan_torrent(item) :
    for enclosure in item.enclosures :
        if enclosure.type != "application/x-bittorrent" :
            continue
        torrent_url = enclosure["href"]
        response = await download_file(torrent_url, "download")
        if not response[0] :
            logger.error(f"下载torrent文件失败: {response[1]}")
            return False, response[1]
        torrent_path = response[1]
        logger.info(f"下载torrent文件, 路径:{torrent_path}")
        return True, torrent_path
    return False, "没有torrent链接"
