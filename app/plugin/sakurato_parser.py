# sakurato_parser.py
import re

from app.models.parser_info import IMatchingStrategy


class SakuratoParser(IMatchingStrategy) :
    @property
    def group_name(self) -> str :
        return "Sakurato"

    def __init__(self) :
        super().__init__()
        # 一些预编译正则可以放这里
        # 以下仅作示例：分成单集、多集两部分
        self.single_episode_patterns = [
            re.compile(
                    r"^\[桜都字幕组]"
                    r"\s(?P<title>.+?)\s"
                    r"\[(?P<episode>\d+)(?:v(?P<version>\d+))?]"
                    r"\[(?P<resolution>\d+[pP])]"
                    r"\[(?P<lang>.+?)]",
                    re.IGNORECASE),
            re.compile(
                    r"^\[桜都字幕組]"
                    r"\s(?P<title>.+?)\s"
                    r"\[(?P<episode>\d+)(?:v(?P<version>\d+))?]"
                    r"\[(?P<resolution>\d+[pP])]"
                    r"\[(?P<lang>.+?)]"
                    r"(?:\s\[(?P<extra>.+?)])?", re.IGNORECASE),
            re.compile(
                    r"^\[Sakurato]"
                    r"\s(?P<title>.+?)\s"
                    r"\[(?P<episode>\d+)(?:v(?P<version>\d+))?]"
                    r"\[(?P<codec>.+?)"
                    r"\s(?P<resolution>\d+[pP])"
                    r"\s(?P<audio>.+?)]"
                    r"\[(?P<lang>.+?)]", re.IGNORECASE),
            re.compile(
                    r"^\[Sakurato]"
                    r"\[(?P<title>.+?)]"
                    r"\[(?P<title_jp>.+?)]"
                    r"\[(?P<episode>\d+)(?:v(?P<version>\d+))?]"
                    r"\[(?P<resolution>\d+[pP])]"
                    r"\[(?P<source>.+?)]"
                    r"\[(?P<format>.+?)]", re.IGNORECASE),
        ]
        self.multiple_episode_patterns = [
            re.compile(
                    r"^\[桜都字幕组]"
                    r"\s(?P<title>.+?)\s"
                    r"\[(?P<start>\d+)"
                    r"(?:v(?P<version1>\d+))?"
                    r"-(?P<end>\d+)"
                    r"(?:v(?P<version2>\d+))?"
                    r"\s*(fin)?(Fin)?]"
                    r"\[(?P<resolution>\d+[pP])]"
                    r"\[(?P<lang>.+?)]", re.IGNORECASE),

            re.compile(
                    r"^\[桜都字幕組]"
                    r"\s(?P<title>.+?)\s"
                    r"\[(?P<start>\d+)"
                    r"(?:v(?P<version1>\d+))?"
                    r"-(?P<end>\d+)"
                    r"(?:v(?P<version2>\d+))?"
                    r"\s*(fin)?(Fin)?]"
                    r"\[(?P<resolution>\d+[pP])]"
                    r"\[(?P<lang>.+?)]", re.IGNORECASE),
            re.compile(
                    r"^\[Sakurato]"
                    r"\[(?P<title>.+?)]"
                    r"\[(?P<title_jp>.+?)]"
                    r"\[(?P<start>\d+)"
                    r"(?:v(?P<version1>\d+))?"
                    r"-(?P<end>\d+)"
                    r"(?:v(?P<version2>\d+))?"
                    r"\s*(fin)?(Fin)?]"
                    r"\[(?P<resolution>\d+[pP])]"
                    r"\[(?P<source>.+?)]"
                    r"\[(?P<format>.+?)]", re.IGNORECASE),
        ]

        # 在某个 parser 里或单独抽出一个 utils.py
        self.language_map = {
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

        self.subtitle_type_map = {
            "内嵌" : "内嵌",
            "内封" : "内封",
        }

    def _detect_language_subtitle(self, lang: str) -> tuple[str, str] :
        lower_lang = lang.lower()

        # 先看 language_map
        # 看 lower_lang 里有没有键，比如 "chs&jpn" 就表示 "简日"
        matched_language = "未知"
        for k, v in self.language_map.items() :
            # 如果 k 能在 lower_lang 里找到（子串匹配），就说明匹配到了这个语言
            # 或者你有更严格的需求的话再改一下匹配方式
            if k.lower() in lower_lang :
                matched_language = v
                break

        # 再看 subtitle_type_map
        matched_subtitle = "内嵌"
        for k, v in self.subtitle_type_map.items() :
            if k in lang :
                matched_subtitle = v
                break

        return matched_language, matched_subtitle
