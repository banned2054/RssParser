# 在某个 parser 里或单独抽出一个 utils.py
import re

from app.models.parser_info import IMatchingStrategy


class NekoMoeParser(IMatchingStrategy) :
    @property
    def group_name(self) -> str :
        return "Nekomoe kissaten"

    def __init__(self) :
        super().__init__()
        self.language_map = {
            "简繁日" : "简繁日",
            "简日"   : "简日",
            "jpsc"   : "简日",
            "繁日"   : "繁日",
            "jptc"   : "简日",
            "简繁"   : "简繁",
        }
        # 一些预编译正则可以放这里
        # 以下仅作示例：分成单集、多集两部分
        self.single_episode_patterns = [
            re.compile(
                    r"^【喵萌奶茶屋】"
                    r"(?:★\d+月新番★)?"
                    r"\[(?P<title>.+?)]"
                    r"\[(?P<episode>\d+)"
                    r"(?:v(?P<version>\d+))?]"
                    r"(?:\[(?P<source>[a-zA-Z]+[Rr]ip)])?"
                    r"\[(?P<resolution>\d+[pP])]"
                    r"\[(?P<lang>.+?)]", re.IGNORECASE),
            re.compile(
                    r"^【喵萌Production】"
                    r"(?:★\d+月新番★)?"
                    r"\[(?P<title>.+?)]"
                    r"\[(?P<episode>\d+)"
                    r"(?:v(?P<version>\d+))?]"
                    r"(?:\[(?P<source>[a-zA-Z]+[Rr]ip)])?"
                    r"\[(?P<resolution>\d+[pP])]"
                    r"\[(?P<lang>.+?)]", re.IGNORECASE),
        ]
        self.multiple_episode_patterns = [
            re.compile(
                    r"^【喵萌奶茶屋】"
                    r"(?:★\d+月新番★)?"
                    r"\[(?P<title>.+?)]"
                    r"\[(?P<start>\d+)"
                    r"(?:v(?P<version1>\d+))?"
                    r"-(?P<end>\d+)"
                    r"(?:v(?P<version2>\d+))?"
                    r"(?:END)?"
                    r"(?:\+(?P<OAD>[a-zA-Z\u4e00-\u9fff]+]))?]"
                    r"(?:\[(?P<source>[a-zA-Z]+[Rr]ip)])?"
                    r"\[(?P<resolution>\d+[pP])]"
                    r"\[(?P<lang>.+?)]", re.IGNORECASE),
            re.compile(
                    r"^【喵萌Production】"
                    r"(?:★\d+月新番★)?"
                    r"\[(?P<title>.+?)]"
                    r"\[(?P<start>\d+)"
                    r"(?:v(?P<version1>\d+))?"
                    r"-(?P<end>\d+)"
                    r"(?:v(?P<version2>\d+))?"
                    r"(?:END)?"
                    r"(?:\+(?P<OAD>[a-zA-Z\u4e00-\u9fff]+))?]"
                    r"(?:\[(?P<source>[a-zA-Z]+[Rr]ip)])?"
                    r"\[(?P<resolution>\d+[pP])]"
                    r"\[(?P<lang>.+?)]", re.IGNORECASE),
        ]

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

        return matched_language, "内嵌"
