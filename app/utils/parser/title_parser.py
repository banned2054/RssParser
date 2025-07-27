import re

from app import config
from app.models.enum.enum_language import EnumLanguage
from app.plugin.ani_parser import AniParser
from app.plugin.nekomoe_parser import NekoMoeParser
from app.plugin.sakurato_parser import SakuratoParser
from app.utils.log_utils import set_up_logger

logger = set_up_logger(__name__)

ani = AniParser()
sakurato = SakuratoParser()
neko_moe = NekoMoeParser()
parser_list = [
    ani,
    sakurato,
    neko_moe,
]
RULES = [
    r"(.*) - (\d{1,4}(?!\d|p)|\d{1,4}\.\d{1,2})(?:v(\d{1,2}))?(?:-\d{1,4}(?:v\d{1,2})?)?(?: )?(?:END)?(.*)",
    r"(.*)[\[\ E](\d{1,4}|\d{1,4}\.\d{1,2})(?:v(\d{1,2}))?(?:-\d{1,4}(?:v\d{1,2})?)?(?: )?(?:END)?[\]\ ](.*)",
    r"(.*)\[(?:第)?(\d+|\d+\.\d+)[话集話](?:-\d+(?:v\d{1,2})?)?(?:END)?\](.*)",
    r"(.*)第?(\d+|\d+\.\d+)[话話集](?:-\d+(?:v\d{1,2})?)?(?:END)?(.*)",
    r"(.*)(?:S\d{2})?EP?(\d+)(?:-\d+(?:v\d{1,2})?)?(.*)",
    r"(.*) - (\d{1,4})(?:\s*\(.*?\))?(?:\s*\[.*?\])?(?:\.mp4)?"
]

SUBTITLE_LANG = {
    "zh-tc"        : ["tc", "cht", "繁体", "繁日", "繁中", "zh-tw", "big5", "baha"],
    "zh-sc"        : ["sc", "chs", "简体", "简日", "简中", "zh", "gb"],
    "zh-sc-and-tc" : ["繁简", "简繁"],
}


def get_subtitle_language(subtitle_name: str) -> str | None :
    result = parser_with_ani_parser(subtitle_name)
    if result is not None :
        if result.group is 'ANi' :
            return 'baha'
        if result.language is EnumLanguage.JpScTc :
            return "zh-sc-and-tc"
        if result.language is EnumLanguage.JpSc :
            return "zh-sc"
        if result.language is EnumLanguage.JpTc :
            return "zh-tc"
        if result.language is EnumLanguage.Sc :
            return "zh-sc"
        if result.language is EnumLanguage.Tc :
            return "zh-tc"
    subtitle_name_lower = subtitle_name.lower()
    if 'lolihouse' in subtitle_name_lower :
        return 'loli'
    if '雪飘工作室' in subtitle_name :
        return 'snow'
    for key, values in SUBTITLE_LANG.items() :
        for v in values :
            if v in subtitle_name_lower :
                return key
    return None


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


def get_title_first_step(origin_title: str) -> str :
    cleared_title = clear_title(origin_title)
    parts = [s for s in re.split(r"[\[\]()【】（）]", cleared_title) if s]
    if len(parts) > 1 :
        if re.match(r"\d+", parts[1]) :
            return cleared_title
        return parts[1]
    return parts[0]


def get_title(origin_title: str) -> str :
    contains_list = config.get_config("contain_filter").split("|")
    for contain_word in contains_list :
        if contain_word.lower() not in origin_title.lower() :
            return ""
    for rule in RULES :
        match = re.match(rule, origin_title, re.I)
        if not match or not match.group(1) :
            continue
        base_title = get_title_first_step(match.group(1)).strip()
        return base_title.split("/")[0].strip()
    return ""


def get_episode(origin_title: str) :
    result = parser_with_ani_parser(origin_title)
    if result is not None :
        if result.is_multiple :
            return result.start_episode, 1, result.episode_number, 1
        return result.episode, result.version, -1, -1
    cleared_title = clear_title(origin_title)
    for rule in RULES :
        if not cleared_title :
            continue
        match = re.match(rule, cleared_title, re.I)
        if not match :
            continue

        episode1 = match.group(2)
        version1 = match.group(3) if match.lastindex and match.lastindex >= 3 and match.group(3) else 1

        ep2_match = re.search(r'-(\d{1,4})(?:v(\d{1,2}))?', match.group(0))
        if ep2_match :
            episode2 = ep2_match.group(1)
            version2 = ep2_match.group(2) if ep2_match.group(2) else 1
        else :
            episode2, version2 = -1, -1

        return int(episode1), int(version1), int(episode2), int(version2)

    return -1, -1, -1, -1


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


def parser_with_ani_parser(title: str) :
    for parser in parser_list :
        result = parser.try_match(title)
        if result[0] :
            return result[1]
    return None
