import re

from app import config
from app.utils.log_utils import set_up_logger

logger = set_up_logger(__name__)

RULES = [
    r"(.*) - (\d{1,4}(?!\d|p)|\d{1,4}\.\d{1,2})(?:v(\d{1,2}))?(?:-\d{1,4}(?:v\d{1,2})?)?(?: )?(?:END)?(.*)",
    r"(.*)[\[\ E](\d{1,4}|\d{1,4}\.\d{1,2})(?:v(\d{1,2}))?(?:-\d{1,4}(?:v\d{1,2})?)?(?: )?(?:END)?[\]\ ](.*)",
    r"(.*)\[(?:第)?(\d+|\d+\.\d+)[话集話](?:-\d+(?:v\d{1,2})?)?(?:END)?\](.*)",
    r"(.*)第?(\d+|\d+\.\d+)[话話集](?:-\d+(?:v\d{1,2})?)?(?:END)?(.*)",
    r"(.*)(?:S\d{2})?EP?(\d+)(?:-\d+(?:v\d{1,2})?)?(.*)",
]

SUBTITLE_LANG = {
    "zh-tc"       : ["tc", "cht", "繁体", "繁日", "繁中", "zh-tw", "big5", "baha"],
    "zh-sc"       : ["sc", "chs", "简体", "简日", "简中", "zh", "gb"],
    "zh-sc-and-tc": ["繁简", "简繁"],
}


def get_subtitle_language(subtitle_name: str) -> str:
    if subtitle_name.lower().__contains__('baha'):
        return 'baha'
    for key, value in SUBTITLE_LANG.items():
        for v in value:
            if v in subtitle_name.lower():
                return key


def clear_title(origin_title):
    """
    清理标题中的特定模式，保留重要信息
    :param str origin_title: 原始标题
    :return str: 清洁后的标题
    """
    # 移除不需要的模式
    patterns = [r"★\d{1,2}月新番★", r"\[招募.*?\]"]

    # 合并模式并编译正则表达式
    pattern = re.compile("|".join(patterns))
    result = pattern.sub("", origin_title).strip()
    result = result.replace('【我推的孩子】 (2024) ', '我推的孩子 第二季')
    result = result.replace('Oshi no Ko (2024) ', 'Oshi no Ko season2')

    return result.strip()


def get_title_first_step(origin_title):
    cleared_title = clear_title(origin_title)
    n = re.split(r"[\[\]()【】（）]", cleared_title)
    while "" in n:
        n.remove("")
    if len(n) > 1:
        if re.match(r"\d+", n[1]):
            return cleared_title
        return n[1]
    else:
        return n[0]


def get_title(origin_title):
    """
    从rss里item的name解析到动画的文件名
    :param str origin_title: item的name
    :return str: 动画的文件名
    """
    contains_list = config.get_config("contain_filter").split("|")
    for contain_word in contains_list:
        if not origin_title.lower().__contains__(contain_word):
            return ""
    for rule in RULES:
        match_obj = re.match(rule, origin_title, re.I)
        if not match_obj or match_obj.group(1) == "":
            continue
        origin_title = get_title_first_step(match_obj.group(1)).strip()
        title = origin_title.split("/")[0]
        title = title.strip()
        return title
    return ""


def get_episode(origin_title):
    """
    从rss里item的name解析到动画的两个集数和版本号
    :param str origin_title: item的name
    :return tuple: 动画的两个集数和版本号 (集数1, 版本号1, 集数2, 版本号2)
    """
    cleared_title = clear_title(origin_title)
    for rule in RULES:
        if not cleared_title:
            continue
        match_obj = re.match(rule, cleared_title, re.I)
        if not match_obj:
            continue

        episode1 = match_obj.group(2)
        version1 = match_obj.group(3) if match_obj.group(3) else 1

        # 匹配第二个集数和版本号
        episode2_match = re.search(r'-(\d{1,4})(?:v(\d{1,2}))?', match_obj.group(0))
        if episode2_match:
            episode2 = episode2_match.group(1)
            version2 = episode2_match.group(2) if episode2_match.group(2) else 1
        else:
            episode2 = -1
            version2 = -1

        return int(episode1), int(version1), int(episode2), int(version2)
    return -1, -1, -1, -1


def universal_replace_name(target, anime_info, episode = None):
    """
    :param str target:
    :param BangumiSubjectInfo anime_info:
    :param float episode:
    :return:
    """
    name = config.get_config(target)
    if name.__contains__("/year/"):
        year = anime_info.pub_date.year
        year_str = f"{year:04d}"
        name = name.replace("/year/", year_str)
    if name.__contains__("/month/"):
        month = anime_info.pub_date.month
        month_str = f"{month:02d}"
        name = name.replace("/month/", month_str)
    if name.__contains__("/day/"):
        day = anime_info.pub_date.day
        day_str = f"{day:02d}"
        name = name.replace("/month/", day_str)
    if name.__contains__("/episode/") and episode is not None:
        # 分解 episode 为整数部分和小数部分
        int_part = int(episode)
        frac_part = episode - int_part

        # 格式化整数部分和小数部分
        if frac_part == 0:
            episode_str = f"{int_part:02d}"
        else:
            episode_str = f"{int_part:02d}.{int(frac_part * 10)}"  # 假设小数部分只有一位
        name = name.replace("/episode/", episode_str)
    name = name.replace("/cn_name/", anime_info.cn_name)
    name = name.replace("/origin_name/", anime_info.origin_name)
    name = name.replace("/id/", str(anime_info.id))
    name = name.replace("/type/", anime_info.now_type.name)
    name = name.replace("/platform/", str(anime_info.platform))
    return name


def clear_title_for_tag(origin_title: str):
    result = origin_title.replace(' ', '_')
    result = result.replace('：', '_')
    result = result.replace(':', '_')
    result = result.replace('.', '_')
    result = result.replace('，', '_')
    result = result.replace(',', '_')
    result = result.replace('。', '_')
    result = result.replace('-', '_')
    result = result.replace('~', '_')
    result = result.replace('“', '_')
    result = result.replace('”', '_')
    result = result.replace('‘', '_')
    result = result.replace('’', '_')
    result = result.replace('"', '_')
    result = result.replace('\'', '_')
    result = result.replace('!', '_')
    result = result.replace('！', '_')
    result = result.replace('?', '_')
    result = result.replace('？', '_')
    result = result.replace('/', '_')
    result = result.replace('\\', '_')
    result = result.replace('[', '')
    result = result.replace('(', '')
    result = result.replace('【', '')
    result = result.replace(')', '')
    result = result.replace(']', '')
    result = result.replace('（', '')
    result = result.replace('】', '')
    result = result.replace('）', '')

    while result.__contains__('__'):
        result = result.replace('__', '_')
    while result.endswith('_'):
        result = result.replace('_', '')
    return result
