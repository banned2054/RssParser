import asyncio
import multiprocessing

from app import config
from app.controllers import bangumi_controller, mikan_controller, temp_controller
from app.controllers.torrent_controller import process_unfinished_downloads
from app.utils.file_utils import create_directory_if_not_exists


def fresh_rss_every_times() :
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(async_fresh_rss_every_times())


async def async_fresh_rss_every_times() :
    sleep_time = int(config.get_config("IntervalTimeToRss"))
    if sleep_time <= 0 :
        sleep_time = 1
    while True :
        await mikan_controller.fresh_rss()
        await bangumi_controller.fresh_rss()
        await temp_controller.fresh_rss()
        await asyncio.sleep(sleep_time)


def fresh_torrent_download_finish() :
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(process_unfinished_downloads())


if __name__ == "__main__" :
    create_directory_if_not_exists('download')

    multiprocessing.set_start_method("spawn", force = True)
    p1 = multiprocessing.Process(target = fresh_rss_every_times)
    p2 = multiprocessing.Process(target = fresh_torrent_download_finish)

    try :
        p1.start()
        p2.start()  # 同时启动第二个进程

        p1.join()  # 等待 p1 进程结束
        p2.join()  # 等待 p2 进程结束
    except KeyboardInterrupt :
        print("检测到Ctrl+C,正在优雅地终止进程...")
        p1.terminate()
        p2.terminate()
        p1.join()  # 确保 p1 进程已经结束
        p2.join()  # 确保 p2 进程已经结束
