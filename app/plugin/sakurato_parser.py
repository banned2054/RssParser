# sakurato_parser.py
import re

from app.models.parser_info import IMatchingStrategy, ParsedInfo

# 在某个 parser 里或单独抽出一个 utils.py
language_map = {
    "简繁日"      : "简繁日",
    "chs&cht&jpn" : "简繁日",
    "简日"        : "简日",
    "chs&jpn"     : "简日",
    "繁日"        : "繁日",
    "cht&jpn"     : "简日",
    "简繁"        : "简繁",
    "chs&cht"     : "简繁",
    "繁体"        : "繁体",
    "繁體"        : "繁体",
    "cht"         : "繁体",
    "简体"        : "简体",
    "chs"         : "简体",
}

subtitle_type_map = {
    "内嵌" : "内嵌",
    "内封" : "内封",
}


def _detect_language_subtitle(lang: str) -> tuple[str, str] :
    lower_lang = lang.lower()

    # 先看 language_map
    # 看 lower_lang 里有没有键，比如 "chs&jpn" 就表示 "简日"
    matched_language = "未知"
    for k, v in language_map.items() :
        # 如果 k 能在 lower_lang 里找到（子串匹配），就说明匹配到了这个语言
        # 或者你有更严格的需求的话再改一下匹配方式
        if k.lower() in lower_lang :
            matched_language = v
            break

    # 再看 subtitle_type_map
    matched_subtitle = "内嵌"
    for k, v in subtitle_type_map.items() :
        if k in lang :
            matched_subtitle = v
            break

    return matched_language, matched_subtitle


class SakuratoParser(IMatchingStrategy) :
    @property
    def group_name(self) -> str :
        return "Sakurato"

    def __init__(self) :
        # 一些预编译正则可以放这里
        # 以下仅作示例：分成单集、多集两部分
        self.single_episode_patterns = [
            re.compile(
                    r"^\[桜都字幕组]\s(?P<title>.+?)\s\[(?P<episode>\d+(?:v\d+)?)]\[(?P<resolution>\d+p)]\[(?P<lang>.+?)]",
                    re.IGNORECASE),
            re.compile(
                    r"^\[桜都字幕組]\s(?P<title>.+?)\s\[(?P<episode>\d+(?:v\d+)?)]\[(?P<resolution>\d+p)]\[(?P<lang>.+?)]("
                    r"?:\s\[(?P<extra>.+?)])?", re.IGNORECASE),
            re.compile(
                    r"^\[Sakurato]\s(?P<title>.+?)\s\[(?P<episode>\d+(?:v\d+)?)]\[(?P<codec>.+?)\s(?P<resolution>\d+p)"
                    r"\s(?P<audio>.+?)]\[(?P<lang>.+?)]", re.IGNORECASE),
            re.compile(
                    r"^\[Sakurato]\[(?P<title>.+?)]\[(?P<title_jp>.+?)]\[(?P<episode>\d+(?:v\d+)?)]"
                    r"\[(?P<resolution>\d+p)]\[(?P<source>.+?)]\[(?P<format>.+?)]", re.IGNORECASE),
        ]
        self.multiple_episode_patterns = [
            re.compile(
                    r"^\[桜都字幕组]\s(?P<title>.+?)\s\[(?P<start>\d+)(?:v\d+)?-(?P<end>\d+)(?:v\d+)?]\[("
                    r"?P<resolution>\d+p)]\[(?P<lang>.+?)]", re.IGNORECASE),

            re.compile(
                    r"^\[桜都字幕組]\s(?P<title>.+?)\s\[(?P<start>\d+)(?:v\d+)?-(?P<end>\d+)(?:v\d+)?]\[("
                    r"?P<resolution>\d+p)]\[(?P<lang>.+?)]", re.IGNORECASE),
            re.compile(
                    r"^\[Sakurato]\[(?P<title>.+?)]\[(?P<title_jp>.+?)]\[(?P<start>\d+)(?:v\d+)?-(?P<end>\d+)(?:v\d+)?"
                    r"(fin)?(Fin)?]\[(?P<resolution>\d+p)]\[(?P<source>.+?)]\[(?P<format>.+?)]", re.IGNORECASE),
        ]

    def try_match(self, filename: str) -> tuple[bool, ParsedInfo | None] :
        # 1) 尝试匹配单集格式
        for pattern in self.single_episode_patterns :
            match = pattern.match(filename)
            if match :
                return True, self._create_parsed_result_single(match)

        # 2) 尝试匹配多集格式
        for pattern in self.multiple_episode_patterns :
            match = pattern.match(filename)
            if match :
                return True, self._create_parsed_result_multiple(match)

        return False, None

    def _create_parsed_result_single(self, match: re.Match) -> ParsedInfo :
        episode_str = match.group("episode")
        episode = int(re.sub(r"\D+", "", episode_str)) if episode_str else -1

        language, subtitle_type = _detect_language_subtitle(match.group("lang"))
        result = ParsedInfo(
                is_multiple = False,
                title = match.group("title").strip(),
                episode = episode,
                source_group = self.group_name,
                resolution = match.group("resolution"),
                language = language,
                subtitle_type = subtitle_type,
        )
        return result

    def _create_parsed_result_multiple(self, match: re.Match) -> ParsedInfo :
        start_str = match.group("start")
        end_str = match.group("end")

        start_episode = int(start_str) if start_str else -1
        end_episode = int(end_str) if end_str else -1

        language, subtitle_type = _detect_language_subtitle(match.group("lang"))
        result = ParsedInfo(
                is_multiple = True,
                title = match.group("title").strip(),
                start_episode = start_episode,
                end_episode = end_episode,
                source_group = self.group_name,
                resolution = match.group("resolution"),
                language = language,
                subtitle_type = subtitle_type,
        )
        return result
