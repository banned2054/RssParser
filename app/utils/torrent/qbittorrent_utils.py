import asyncio
import traceback

import qbittorrentapi

from app import config
from app.models.sql import RssItemTable
from app.utils.file_utils import remove_file
from app.utils.log_utils import set_up_logger
from app.utils.parser.title_parser import clear_title
from app.utils.telegram_utils import send_message
from app.utils.torrent.torrent_utils import get_torrent_file_len, get_torrent_info_hash

qbt_client = qbittorrentapi.Client(
        host = config.get_config("qbittorrent_url"),
        username = config.get_config("qbittorrent_username"),
        password = config.get_config("qbittorrent_password"),
)
logger = set_up_logger(__name__)


async def send_notification(item_info) :
    try :
        await send_message(
                f"标题:{item_info.item_name}\n"
                f"发布时间:{item_info.pub_date}\n"
                f"原始标题{clear_title(item_info.origin_name)}\n"
                f"mikan地址:{config.mikan_episode}{item_info.mikan_url}\n"
                f"bgm地址:https://bgm.tv/subject/{item_info.bangumi_id}"
        )
    except Exception as e :
        logger.error(e)


async def download_one_file(
        torrent_path,
        new_torrent_name,
        save_path,
        dir_name,
        file_name,
        tag,
        item_info,
) :
    """
    添加种子到qbittorrent
    :param new_torrent_name:
    :param item_info:
    :param str torrent_path: torrent文件的路径
    :param str save_path: 下载的路径，例如`/downloads/Anime`
    :param str dir_name: 下载的动画的文件夹，例如`[2023.01]白圣女与黑牧师`
    :param str file_name: 下载的单集动画名，例如`白圣女与黑牧师 E01.mp4`
    :param str tag:
    :return:
    """
    try :
        torrent_hash = get_torrent_info_hash(torrent_path)
        flag = check_torrent_exist(torrent_hash)
        if flag :
            logger.info("torrent已添加")
            await torrent_already_add(
                    torrent_hash,
                    torrent_path,
                    new_torrent_name,
                    dir_name,
                    file_name,
                    tag,
                    item_info
            )
            return
        now_len = get_torrent_file_len(torrent_path)
        if now_len > 1 :
            await send_message('出现多文件:\n'
                               f'标题：{clear_title(item_info.origin_name)}\n'
                               f'链接:https://mikanani.me/Home/Episode/{item_info.mikan_url}')

            RssItemTable.insert_rss_data(item_info, "error", True)
            raise Exception(
                    f"this torrent is not download one file:{item_info.origin_name}"
            )

        await send_notification(item_info)

        with open(torrent_path, "rb") as f :
            torrent_content = f.read()
        # 一开始就暂停下载，方便改名字
        qbt_client.torrents_add(
                torrent_files = torrent_content, savepath = save_path, is_paused = True
        )
        await asyncio.sleep(2)

        logger.info(f"torrent添加成功，hash:{torrent_hash}")
        await after_add_torrent(
                torrent_path,
                torrent_hash,
                new_torrent_name,
                dir_name,
                file_name,
                tag,
                item_info
        )
    except Exception as e :
        error_str = str(e)
        tb = traceback.extract_tb(e.__traceback__)
        filename = tb[-1].filename
        lineno = tb[-1].lineno
        logger.error(
                f"Try to add qbittorrent torrent failed: {error_str}; file name: {filename}, line: {lineno}"
        )


async def torrent_already_add(
        torrent_hash, torrent_path, new_torrent_name, dir_name, file_name, tag, item_info
) :
    await after_add_torrent(
            torrent_path,
            torrent_hash,
            new_torrent_name,
            dir_name,
            file_name,
            tag,
            item_info,
    )
    # 可能还需要处理 torrent_hash 为空的情况
    if not RssItemTable.check_item_exist(item_info.mikan_url) :
        RssItemTable.insert_rss_data(item_info, torrent_hash)


async def after_add_torrent(
        torrent_path,
        torrent_hash,
        new_torrent_name,
        dir_name,
        file_name,
        tag,
        item_info,
) :
    try :
        # 重命名qbittorrent里的种子名
        qbt_client.torrents_rename(
                torrent_hash = torrent_hash, new_torrent_name = new_torrent_name
        )
        # 更改文件名
        files = qbt_client.torrents_files(torrent_hash = torrent_hash)
        if dir_name[-1] == "/" :
            dir_name = dir_name[:-1]
        new_file_name = f'{dir_name}/{file_name}.{files[0].name.split(".")[-1]}'
        qbt_client.torrents_rename_file(
                torrent_hash = torrent_hash, file_id = 0, new_file_name = new_file_name
        )
        qbt_client.torrents_add_tags(torrent_hashes = torrent_hash, tags = tag)
        # 重新检查文件是否下载完成
        qbt_client.torrents_recheck(torrent_hash)
        logger.debug(f"Torrent rechecked.")
        status = get_torrent_status(torrent_hash)
        while status.startswith('checking') :
            await asyncio.sleep(1)
            status = get_torrent_status(torrent_hash)
        logger.debug(f'Torrent status: {status}')
        await asyncio.sleep(1)
        # 继续下载
        resume_torrent(torrent_hash)
        await asyncio.sleep(1)
        status = get_torrent_status(torrent_hash)
        logger.debug(f'Torrent status: {status}')
        logger.debug(f"Torrent resume.")

        qbt_client.torrents_reannounce(torrent_hashes = torrent_hash)
        RssItemTable.insert_rss_data(item_info, torrent_hash)
        remove_file(torrent_path)
    except :
        pass


def resume_torrent(torrent_hash) :
    qbt_client.torrents_resume(torrent_hash)


def check_torrent_finish_download(torrent_hash) :
    try :
        state = get_torrent_status(torrent_hash)
        progress = get_torrent_progress(torrent_hash)

        if state == "uploading" or progress == 1 :
            return True
        else :
            return False

    except Exception as e :
        print(f"An error occurred: {e}")
        return False


def get_torrent_progress(torrent_hash) :
    try :
        torrent_info = qbt_client.torrents_info(hashes = torrent_hash)

        if not torrent_info :
            print(f"No torrent found with hash: {torrent_hash}")
            raise Exception(f'torrent: {torrent_hash} not find')

        return torrent_info[0].progress

    except qbittorrentapi.exceptions.LoginFailed :
        print("Login failed! Please check your qBittorrent credentials.")
        return False
    except Exception as e :
        print(f"An error occurred: {e}")
        return False


def get_torrent_status(torrent_hash) :
    try :
        torrent_info = qbt_client.torrents_info(hashes = torrent_hash)

        if not torrent_info :
            print(f"No torrent found with hash: {torrent_hash}")
            raise Exception(f'torrent: {torrent_hash} not find')

        return torrent_info[0].state

    except qbittorrentapi.exceptions.LoginFailed :
        print("Login failed! Please check your qBittorrent credentials.")
        return False
    except Exception as e :
        print(f"An error occurred: {e}")
        return False


def check_torrent_exist(torrent_hash) :
    try :
        # 尝试获取 torrent 的信息
        torrent_info = qbt_client.torrents_info(torrent_hashes = torrent_hash)

        if torrent_info :
            return True
        else :
            return False
    except Exception as e :
        return False


def delete_torrent_by_hash(torrent_hash) :
    try :
        # 获取当前存在的种子信息
        torrents = qbt_client.torrents.info()
        # 检查是否存在该 hash 的种子
        if any(torrent.hash.lower() == torrent_hash.lower() for torrent in torrents) :
            # 删除种子但保留文件
            qbt_client.torrents_delete(delete_files = False, torrent_hashes = torrent_hash)
            logger.debug(f"删除旧版本种子，hash:{torrent_hash}")
    except qbittorrentapi.exceptions.APIError as e :
        logger.error(f"Failed to delete torrent with hash {torrent_hash}: {e}")
