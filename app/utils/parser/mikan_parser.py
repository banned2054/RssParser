from bs4 import BeautifulSoup

from app import config
from app.utils.log_utils import set_up_logger
from app.utils.net_utils import fetch

logger = set_up_logger(__name__)


async def get_bangumi_url_from_mikan(mikan_url) :
    """
    解析html信息，从单部动画在mikan上的页面解析到对应的该动画在bangumi地址
    :param str mikan_url: mikan上单部动画的页面的地址在Bangumi/后面的部分
    :return tuple[bool, str]: 该动画对应的bangumi地址
    """
    try :
        response = await fetch(f"{config.mikan_home}{mikan_url}")
        if response[0] :
            soup = BeautifulSoup(response[1], 'html.parser')
            a_tag = soup.select_one('p.bangumi-info > a[href*="bgm.tv"]')
            if a_tag :
                href = a_tag['href']
                logger.debug(f"Get bangumi url from mikan page: {href}")
                return True, href
            else :
                raise Exception("No href found")
        else :
            raise Exception("Fetch failed")
    except Exception as e :
        error_str = str(e)
        logger.error(f"Try to get bangumi url from mikan page failed: {error_str}")
        return False, error_str


async def get_anime_home_url_from_mikan(mikan_url) :
    """
    解析html信息，从单集动画在mikan上的页面解析到对应的该动画在mikan上的home地址
    :param str mikan_url: mikan上单集动画的页面的地址在Episode/后面的部分
    :return tuple[bool, str]: 该动画对应的home地址
    """
    try :
        response = await fetch(f"{config.mikan_episode}{mikan_url}")
        if response[0] :
            soup = BeautifulSoup(response[1], 'html.parser')
            a_tag = soup.select_one('p.bangumi-title > a')
            if a_tag :
                href = a_tag['href']
                logger.debug(f"Get anime home url from mikan page: https://mikanani.me{href}")
                return True, href.split("/Home/Bangumi/")[-1]
            else :
                raise Exception("No href found")
        else :
            raise Exception("Fetch failed")
    except Exception as e :
        error_str = str(e)
        logger.error(f"Try to get anime home url from mikan page failed: {error_str}")
        return False, error_str
