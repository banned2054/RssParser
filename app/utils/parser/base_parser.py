import re
from abc import ABC, abstractmethod
from typing import List, Optional, Pattern, Tuple

from app.models.enum.enum_group_type import EnumGroupType
from app.models.enum.enum_language import EnumLanguage
from app.models.enum.enum_resolution import EnumResolution
from app.models.enum.enum_subtitle_type import EnumSubtitleType
from app.models.parser_result import ParseResult


def replace_with_regex(text: str, mapping: List[Tuple[str, str]]) -> str :
    """将字符串根据正则映射批量替换"""
    for pattern, replacement in sorted(mapping, key = lambda x : len(x[0]), reverse = True) :
        if re.search(pattern, text, re.IGNORECASE) :
            return replacement
    return text


class BaseParser(ABC) :
    def __init__(self) :
        self.language_map: dict[str, EnumLanguage] = {
            "简繁日"      : EnumLanguage.JpScTc,
            "Chs&Cht&Jpn" : EnumLanguage.JpScTc,
            "简日"        : EnumLanguage.JpSc,
            "Chs&Jpn"     : EnumLanguage.JpSc,
            "JpSc"        : EnumLanguage.JpSc,
            "繁日"        : EnumLanguage.JpTc,
            "Cht&Jpn"     : EnumLanguage.JpTc,
            "JpTc"        : EnumLanguage.JpTc,
            "简繁"        : EnumLanguage.ScTc,
            "Chs&Cht"     : EnumLanguage.ScTc,
            "Cht&Chs"     : EnumLanguage.ScTc,
            "简体"        : EnumLanguage.Sc,
            "Chs"         : EnumLanguage.Sc,
            "繁体"        : EnumLanguage.Tc,
            "繁體"        : EnumLanguage.Tc,
            "Cht"         : EnumLanguage.Tc,
            "GB"          : EnumLanguage.Sc,
            "BIG5"        : EnumLanguage.Sc,
        }
        self.subtitle_type_map: dict[str, EnumSubtitleType] = {
            "内嵌" : EnumSubtitleType.Embedded,
            "內嵌" : EnumSubtitleType.Embedded,
            "內封" : EnumSubtitleType.Embedded,
            "内封" : EnumSubtitleType.Muxed,
            "外挂" : EnumSubtitleType.External,
        }
        self.group_name_map: List[Tuple[str, str]] = [
            (r"(?:Sakurato|[樱桜]都字幕[組组])", "桜都字幕组"),
            (r"(?:喵萌Production|Nekomoe\skissaten)", "喵萌奶茶屋"),
            (r"STYHSub", "霜庭云花"),
            (r"(?:DMG|動漫國字幕組)", "动漫国字幕组"),
            (r"FLsnow", "雪飘工作室"),
            (r"Haruhana", "拨雪寻春"),
            (r"KitaujiSub", "北宇治字幕组"),
            (r"MingY&", "MingYSub"),
            (r"Billion\sMeta\sLab", "亿次研同好会"),
        ]

        self.filter_list: List[str] = []
        self.single_episode_patterns: List[Pattern] = []
        self.multiple_episode_patterns: List[Pattern] = []

    @property
    @abstractmethod
    def group_name(self) -> str :
        pass

    @property
    @abstractmethod
    def group_type(self) -> EnumGroupType :
        pass

    def try_match(self, file_name: str) -> Tuple[bool, Optional[ParseResult]] :
        file_name = file_name.strip()
        if not file_name :
            return False, None

        for filter_pattern in self.filter_list :
            if re.search(filter_pattern, file_name, re.IGNORECASE) :
                return False, None

        for pattern in self.multiple_episode_patterns :
            match = re.match(pattern, file_name)
            if match :
                result = self.create_parsed_result_multiple(match)
                result.group = replace_with_regex(result.group, self.group_name_map)
                return True, result

        for pattern in self.single_episode_patterns :
            match = re.match(pattern, file_name)
            if match :
                result = self.create_parsed_result_single(match)
                result.group = replace_with_regex(result.group, self.group_name_map)
                return True, result

        return False, None

    def create_parsed_result_single(self, match: re.Match) -> ParseResult :
        episode_str = match.groupdict().get("episode", "")
        episode = int(re.sub(r"\D+", "", episode_str)) if episode_str else None

        lang_str = match.groupdict().get("lang", "")
        resolution_str = match.groupdict().get("resolution", "")
        title = str(match.groupdict().get("title", "")).strip()

        lang, sub_type = self.detect_language_subtitle(lang_str)

        return ParseResult(
                is_multiple = False,
                title = title,
                episode = episode,
                group = self.group_name,
                resolution = EnumResolution.from_string(resolution_str),
                language = lang,
                subtitle_type = sub_type,
        )

    def create_parsed_result_multiple(self, match: re.Match) -> ParseResult :
        start = match.groupdict().get("start", "")
        end = match.groupdict().get("end", "")

        start_ep = int(re.sub(r"\D+", "", start)) if start else None
        end_ep = int(re.sub(r"\D+", "", end)) if end else None

        lang_str = match.groupdict().get("lang", "")
        resolution_str = match.groupdict().get("resolution", "")
        title = str(match.groupdict().get("title", "")).strip()

        lang, sub_type = self.detect_language_subtitle(lang_str)

        return ParseResult(
                is_multiple = True,
                title = title,
                start_episode = start_ep,
                end_episode = end_ep,
                group = self.group_name,
                group_type = self.group_type,
                resolution = EnumResolution.from_string(resolution_str),
                language = lang,
                subtitle_type = sub_type,
        )

    def detect_language_subtitle(self, text: str) -> Tuple[EnumLanguage, EnumSubtitleType] :
        lower = text.lower().strip()
        lang = EnumLanguage.Unknown
        sub = EnumSubtitleType.Unknown

        for k, v in sorted(self.language_map.items(), key = lambda kv : len(kv[0]), reverse = True) :
            if k.lower() in lower :
                lang = v
                break

        for k, v in sorted(self.subtitle_type_map.items(), key = lambda kv : len(kv[0]), reverse = True) :
            if k.lower() in lower :
                sub = v
                break

        return lang, sub
