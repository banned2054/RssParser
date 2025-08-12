import re

from pyaniparser import AniParser

from app import config
from app.utils.log_utils import set_up_logger

logger = set_up_logger(__name__)

ani = AniParser()


def clear_title(origin_title: str) -> str :
    patterns = [r"★\d{1,2}月新番★", r"\[招募.*?\]"]
    result = re.sub("|".join(patterns), "", origin_title).strip()

    replace_dict = {
        '【我推的孩子】 (2024) '          : '我推的孩子 第二季',
        'Oshi no Ko (2024) '            : 'Oshi no Ko season2',
        '【喵萌奶茶屋】'                  : '[喵萌奶茶屋]',
        '  '                            : ' ',
        '[WEB-DL]'                      : '',
        '[AAC AVC]'                     : '',
        '[WebRip 1080p HEVC-10bit AAC]' : '',
        '[MP4]'                         : '',
        '[WebRip]'                      : ''
    }

    for old, new in replace_dict.items() :
        result = result.replace(old, new)

    return result.strip()


def universal_replace_name(target, anime_info, episode = None) :
    name = config.get_config(target)

    if "/year/" in name :
        name = name.replace("/year/", f"{anime_info.pub_date.year:04d}")
    if "/month/" in name :
        name = name.replace("/month/", f"{anime_info.pub_date.month:02d}")
    if "/day/" in name :
        name = name.replace("/day/", f"{anime_info.pub_date.day:02d}")
    if "/episode/" in name and episode is not None :
        int_part = int(episode)
        frac_part = episode - int_part
        episode_str = f"{int_part:02d}" if frac_part == 0 else f"{int_part:02d}.{int(frac_part * 10)}"
        name = name.replace("/episode/", episode_str)

    name = name.replace("/cn_name/", anime_info.cn_name)
    name = name.replace("/origin_name/", anime_info.origin_name)
    name = name.replace("/id/", str(anime_info.id))
    name = name.replace("/type/", anime_info.now_type.name)
    name = name.replace("/platform/", str(anime_info.platform))

    return name


def clear_title_for_tag(origin_title: str) -> str :
    result = re.sub(r"[：:，,。\-~“”‘’\"\'!！?？/\\\s]", "_", origin_title)
    result = re.sub(r'[\[(【)\]】）]', "", result)
    result = re.sub(r"_+", "_", result)
    return result.strip("_")
