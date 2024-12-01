import asyncio

from app import config
from app.models.sql import BangumiTable, RssItemTable
from app.utils.log_utils import set_up_logger
from app.utils.parser.title_parser import clear_title_for_tag
from app.utils.telegram_utils import send_message_to_channel
from app.utils.torrent.qbittorrent_utils import check_torrent_finish_download, get_torrent_status, resume_torrent

logger = set_up_logger(__name__)

RETRY_DELAY = 60  # 秒


async def handle_single_download(unfinished_download_hash) :
    """处理单个下载项"""
    try :
        result = check_torrent_finish_download(unfinished_download_hash)
        if not result :
            status = get_torrent_status(unfinished_download_hash)
            if status.startswith('paused') :
                resume_torrent(unfinished_download_hash)
            return

        item_info_result = RssItemTable.get_item_info_by_hash(unfinished_download_hash)
        if not item_info_result[0] :
            return

        logger.info(f'Torrent [{item_info_result[1].item_name}] 下载完成，hash: {unfinished_download_hash}')
        await send_download_complete_message(item_info_result[1])
        RssItemTable.finish_item_download(unfinished_download_hash)
    except Exception as e :
        logger.error(f"处理单个下载失败: {e}")


async def send_download_complete_message(item) :
    """发送下载完成的消息"""
    try :
        bangumi_subject_id = item.bangumi_id
        name_cn = BangumiTable.get_anime_name_by_id(bangumi_subject_id)[1]
        name_cn = clear_title_for_tag(name_cn)
        await send_message_to_channel(
                f"下载完成！\n"
                f"标题: {item.item_name}\n"
                f"发布时间: {item.pub_date}\n"
                f"mikan地址: {config.mikan_episode}{item.mikan_url}\n"
                f"bgm地址: https://bgm.tv/subject/{item.bangumi_id}\n"
                f"#tv #{name_cn}"
        )
    except Exception as e :
        logger.error(f"发送下载完成消息失败: {e}")


async def process_unfinished_downloads() :
    while True :
        try :
            unfinished_download_hash_list = RssItemTable.get_not_finished_download_item()
            for unfinished_download_hash in unfinished_download_hash_list :
                await handle_single_download(unfinished_download_hash)
        except Exception as e :
            logger.error(f"处理未完成种子失败: {e}")
        await asyncio.sleep(RETRY_DELAY)
