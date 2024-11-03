import feedparser

from app import config
from app.controllers import mikan_controller
from app.utils.log_utils import set_up_logger
from app.utils.net_utils import fetch

logger = set_up_logger(__name__)


async def fresh_rss():
    temp_list = config.get_temp_rss()
    if len(temp_list) == 0:
        return
    for temp_rss in temp_list:
        if temp_rss == '':
            continue
        rss_page = await fetch(temp_rss)
        logger.info("fetch temp rss")
        feed = feedparser.parse(rss_page[1])
        # 查询每一个item
        for item in reversed(feed.entries):
            await mikan_controller.analyze_item(item)
    config.clear_temp_rss()
