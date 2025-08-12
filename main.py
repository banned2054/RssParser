import asyncio
import logging
import multiprocessing as mp
import sys
from multiprocessing.synchronize import Event as MpEvent  # 关键：正确的类型

from app import config
from app.controllers import bangumi_controller, mikan_controller, temp_controller
from app.controllers.torrent_controller import process_unfinished_downloads
from app.utils.file_utils import create_directory_if_not_exists


# ---------------- workers (async) ----------------

async def _wait_or_shutdown(shutdown_event: MpEvent, timeout: float) -> bool :
    """在 asyncio 中等待 shutdown_event 或超时；返回 True 表示收到了关闭信号。"""
    try :
        # event.wait() 是阻塞的，同步调用放到线程里等待，并设置超时
        ok = await asyncio.wait_for(asyncio.to_thread(shutdown_event.wait), timeout = timeout)
        return bool(ok)
    except asyncio.TimeoutError :
        return False


async def rss_worker(shutdown_event: MpEvent, interval_sec: int) -> None :
    interval_sec = max(1, int(interval_sec))
    while not shutdown_event.is_set() :
        results = await asyncio.gather(
                mikan_controller.fresh_rss(),
                bangumi_controller.fresh_rss(),
                temp_controller.fresh_rss(),
                return_exceptions = True
        )
        for r in results :
            if isinstance(r, Exception) :
                logging.exception("RSS 刷新子任务异常", exc_info = r)

        if await _wait_or_shutdown(shutdown_event, interval_sec) :
            break


async def torrent_worker(shutdown_event: MpEvent, interval_sec: int) -> None :
    interval_sec = max(1, int(interval_sec))
    while not shutdown_event.is_set() :
        try :
            await process_unfinished_downloads()
        except Exception :
            logging.exception("处理未完成下载时异常")

        if await _wait_or_shutdown(shutdown_event, interval_sec) :
            break


# ---------------- process targets (sync) ----------------

def run_rss(shutdown_event: MpEvent) -> None :
    raw = config.get_config("interval_time_to_rss")
    try :
        interval = int(raw)
    except Exception :
        interval = 1
    interval = max(1, interval)
    asyncio.run(rss_worker(shutdown_event, interval))


def run_torrent(shutdown_event: MpEvent) -> None :
    # 如需可配置可改成从 config 取
    interval = 10
    asyncio.run(torrent_worker(shutdown_event, interval))


# ---------------- main ----------------

def main() -> None :
    logging.basicConfig(
            level = logging.INFO,
            format = "%(asctime)s %(processName)s %(levelname)s: %(message)s"
    )
    create_directory_if_not_exists("download")

    # Windows 用 spawn；POSIX 用默认
    if sys.platform.startswith("win") :
        ctx = mp.get_context("spawn")
    else :
        ctx = mp.get_context()

    shutdown = ctx.Event()

    procs = [
        ctx.Process(target = run_rss, name = "RSSWorker", args = (shutdown,)),
        ctx.Process(target = run_torrent, name = "TorrentWorker", args = (shutdown,))
    ]

    for p in procs :
        p.start()

    try :
        for p in procs :
            p.join()
    except KeyboardInterrupt :
        logging.info("检测到 Ctrl+C，正在优雅退出…")
        shutdown.set()
        for p in procs :
            p.join(timeout = 10)

        # 兜底强杀仍存活的进程
        for p in procs :
            if p.is_alive() :
                logging.warning("进程仍存活，执行强制终止: %s", p.name)
                p.terminate()
        for p in procs :
            p.join()


if __name__ == "__main__" :
    mp.freeze_support()
    main()
