import time

from app import config
from app.models.sql import BangumiTable, RssItemTable
from app.utils.parser.title_parser import clear_title, clear_title_for_tag
from app.utils.qbittorrent_utils import check_torrent_finish_download
from app.utils.telegram_utils import send_message_to_channel


async def handle_single_download(unfinished_download_hash):
    """处理单个下载项"""
    result = check_torrent_finish_download(unfinished_download_hash)
    if not result:
        return
    item_info_result = RssItemTable.get_item_info_by_hash(unfinished_download_hash)
    if not item_info_result[0]:
        return
    await send_download_complete_message(item_info_result[1])
    RssItemTable.finish_item_download(unfinished_download_hash)


async def send_download_complete_message(item):
    """发送下载完成的消息"""
    bangumi_subject_id = item.bangumi_id
    name_cn = BangumiTable.get_anime_name_by_id(bangumi_subject_id)[1]
    name_cn = clear_title_for_tag(name_cn)
    await send_message_to_channel(
            "下载完成！\n"
            f"标题:{item.item_name}\n"
            f"发布时间:{item.pub_date}\n"
            f"原始标题{clear_title(item.origin_name)}\n"
            f"mikan地址:{config.mikan_episode}{item.mikan_url}\n"
            f"bgm地址:https://bgm.tv/subject/{item.bangumi_id}\n"
            f"#tv #{name_cn}"
    )


async def check_unfinished_downloads_every_minute():
    """每分钟检查未完成的下载"""
    while True:
        unfinished_download_hash_list = RssItemTable.get_not_finished_download_item()
        for unfinished_download_hash in unfinished_download_hash_list:
            await handle_single_download(unfinished_download_hash)
        time.sleep(60)
