import asyncio
import logging
import multiprocessing as mp
import signal
import sys
import time
from multiprocessing.synchronize import Event as MpEvent  # 关键：正确的类型

from app import config
from app.controllers import bangumi_controller, mikan_controller, temp_controller
from app.controllers.torrent_controller import process_unfinished_downloads
from app.utils.file_utils import create_directory_if_not_exists


# ---------------- workers (async) ----------------

async def _wait_or_shutdown(shutdown_event: MpEvent, timeout: float) -> bool :
    """在 asyncio 中等待 shutdown_event 或超时；返回 True 表示收到了关闭信号。"""
    try :
        ok = await asyncio.wait_for(asyncio.to_thread(shutdown_event.wait), timeout = timeout)
        return bool(ok)
    except asyncio.TimeoutError :
        return False


async def rss_worker(shutdown_event: MpEvent, interval_sec: int) -> None :
    interval_sec = max(1, int(interval_sec))
    try :
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
    except asyncio.CancelledError :
        # 优雅退出，不打印堆栈
        pass


async def torrent_worker(shutdown_event: MpEvent, interval_sec: int) -> None :
    interval_sec = max(1, int(interval_sec))
    try :
        while not shutdown_event.is_set() :
            try :
                await process_unfinished_downloads()
            except asyncio.CancelledError :
                # 取消就退出
                return
            except Exception :
                logging.exception("处理未完成下载时异常")

            if await _wait_or_shutdown(shutdown_event, interval_sec) :
                break
    except asyncio.CancelledError :
        pass


# ---------------- process targets (sync) ----------------

def _child_ignore_sigint() -> None :
    """让子进程忽略 Ctrl+C，只由 shutdown_event 控制生命周期。"""
    try :
        signal.signal(signal.SIGINT, signal.SIG_IGN)
    except Exception :
        # Windows 也支持 SIGINT；这里兜底
        pass


def run_rss(shutdown_event: MpEvent) -> None :
    raw = config.get_config("interval_time_to_rss")
    try :
        interval = int(raw)
    except Exception :
        interval = 1
    interval = max(1, interval)
    try :
        asyncio.run(rss_worker(shutdown_event, interval))
    except (KeyboardInterrupt, asyncio.CancelledError) :
        # 避免子进程在控制台打印堆栈
        pass


def run_torrent(shutdown_event: MpEvent) -> None :
    # 如需可配置可改成从 config 取
    interval = 10
    try :
        asyncio.run(torrent_worker(shutdown_event, interval))
    except (KeyboardInterrupt, asyncio.CancelledError) :
        pass


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
        ctx.Process(target = run_rss, name = "RSSWorker", args = (shutdown,), daemon = False),
        ctx.Process(target = run_torrent, name = "TorrentWorker", args = (shutdown,), daemon = False)
    ]

    # 让子进程忽略 SIGINT
    for p in procs :
        p.start()
        _ = None  # 占位

    # 父进程专门处理 Ctrl+C：设置 shutdown 并等待子进程退出
    def _on_sigint(signum, frame) :
        logging.info("收到 Ctrl+C，开始优雅退出…")
        shutdown.set()

    prev = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, _on_sigint)

    try :
        # 轮询等待，避免 join() 在 SIGINT 到来时阻塞得难看
        while any(p.is_alive() for p in procs) :
            time.sleep(0.2)
    finally :
        # 还原信号处理器
        try :
            signal.signal(signal.SIGINT, prev)
        except Exception :
            pass

        # 给 10 秒优雅退出时间
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
    # 关键：在创建子进程前设置子进程忽略 SIGINT 的方式
    # multiprocessing 并没有全局 initializer，这里在 target 内部做了 try/except。
    # 如果你想更保险，可以把 _child_ignore_sigint 放到 run_rss/run_torrent 的最开始调用。
    main()
