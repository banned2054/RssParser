# 在某个 parser 里或单独抽出一个 utils.py
import re

from app.models.enum.enum_group_type import EnumGroupType
from app.models.enum.enum_language import EnumLanguage
from app.models.enum.enum_resolution import EnumResolution
from app.models.enum.enum_subtitle_type import EnumSubtitleType
from app.models.parser_result import ParseResult
from app.utils.parser.base_parser import BaseParser


class AniParser(BaseParser) :
    @property
    def group_name(self) -> str :
        return "ANi"

    @property
    def group_type(self) -> EnumGroupType :
        return EnumGroupType.Transfer

    def __init__(self) :
        super().__init__()
        self.language_map["CHT CHS"] = EnumLanguage.ScTc
        self.subtitle_type_map["CHT CHS"] = EnumSubtitleType.Muxed
        self.subtitle_type_map["CHT"] = EnumSubtitleType.Embedded
        self.subtitle_type_map["CHS"] = EnumSubtitleType.Embedded

        self.single_episode_patterns = [
            re.compile(
                    r"\[ANi](?P<title>[^\[\]]+?)-\s?(?P<episode>\d+)(?:v(?P<version>\d+))?\s?\[(?P<resolution>\d+p)]\[(?P<websource>Baha)]\[(?P<source>WEB-DL)]\[(?P<codeA>AAC)\s(?P<codeV>AVC)]\[(?P<lang>.+?)]",
                    re.IGNORECASE
            ),
        ]

    def detect_language_subtitle(self, lang: str) -> tuple[EnumLanguage, EnumSubtitleType] :
        lower_lang = lang.lower().strip()
        language = EnumLanguage.Unknown
        subtitle_type = EnumSubtitleType.Embedded  # 默认值

        for k, v in sorted(self.language_map.items(), key = lambda kv : len(kv[0]), reverse = True) :
            if k.lower() in lower_lang :
                language = v
                break

        for k, v in sorted(self.subtitle_type_map.items(), key = lambda kv : len(kv[0]), reverse = True) :
            if k.lower() in lower_lang :
                subtitle_type = v
                break

        return language, subtitle_type

    def create_parsed_result_single(self, match: re.Match) -> ParseResult :
        episode_str = match.groupdict().get("episode", "0")
        episode = int(re.sub(r"\D+", "", episode_str)) if episode_str else None

        lang_str = match.groupdict().get("lang", "")
        resolution_str = match.groupdict().get("resolution", "")
        title = str(match.groupdict().get("title", "")).strip()
        web_source = str(match.groupdict().get("websource", "")).strip()
        source = str(match.groupdict().get("source", "")).strip()

        lang, sub_type = self.detect_language_subtitle(lang_str)

        version = int(match.groupdict().get("version", '1') or '1')
        return ParseResult(
                is_multiple = False,
                title = title,
                episode = episode,
                version = version,
                group = self.group_name,
                group_type = self.group_type,
                resolution = EnumResolution.from_string(resolution_str),
                language = lang,
                subtitle_type = sub_type,
                web_source = web_source,
                source = source
        )
