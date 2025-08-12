import feedparser
from pyaniparser import AniParser
from pyaniparser.types import EnumMediaType

from app import config
from app.controllers.mikan_controller import download_and_notify, handle_exception, process_existing_bangumi_item, \
    process_new_bangumi_item, should_skip_item
from app.models.sql import BangumiTable, RssItemTable
from app.utils.log_utils import set_up_logger
from app.utils.net_utils import download_file, fetch

logger = set_up_logger(__name__)
parser = AniParser()


async def fresh_rss() :
    try :
        subscription_list = config.bangumi_subscription
        for subscription in subscription_list :
            # 访问rss链接，并解析
            rss_page = await fetch(subscription.rss_url)
            logger.info("fetch rss")
            feed = feedparser.parse(rss_page[1])

            # 查询每一个item
            for item in reversed(feed.entries) :
                print(item)
                await analyze_item(item, subscription.subject_id)
    except Exception as e :
        handle_exception(e)
        return False, str(e)


async def analyze_item(item, subject_id) :
    if subject_id == -1 :
        return
    item_title = item.title
    should_skip, now_language = should_skip_item(item_title)
    if should_skip :
        return

    parseResult = parser.parse(item_title)
    origin_title = parseResult.title
    if origin_title == "" :
        return
    moe_url = ''
    for enclosure in item['links'] :
        if enclosure.type != "text/html" :
            continue
        moe_url = enclosure['href']
        break
    if moe_url == "" :
        return

    if RssItemTable.check_item_exist(moe_url) :
        return

    logger.info(f"add new torrent: {item.title}")
    if parseResult.media_type is EnumMediaType.MultipleEpisode :
        episode = parseResult.start_episode
    else :
        episode = parseResult.episode
    version = parseResult.version

    if BangumiTable.check_anime_exists(subject_id) :
        anime_info, item_info = await process_existing_bangumi_item(item, subject_id, episode, origin_title,
                                                                    item_title,
                                                                    moe_url, version)
    else :
        anime_info, item_info = await process_new_bangumi_item(item, subject_id, episode, origin_title,
                                                               item_title,
                                                               moe_url, version)
    torrent_result = await download_moe_torrent(item)
    if not torrent_result[0] :
        return
    await download_and_notify(torrent_result[1], anime_info, item_info, now_language)


async def download_moe_torrent(item) :
    for enclosure in item['links'] :
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
