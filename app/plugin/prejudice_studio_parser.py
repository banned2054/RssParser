# 在某个 parser 里或单独抽出一个 utils.py
import re

from app.models.enum.enum_group_type import EnumGroupType
from app.models.enum.enum_language import EnumLanguage
from app.models.enum.enum_resolution import EnumResolution
from app.models.parser_result import ParseResult
from app.utils.parser.base_parser import BaseParser


class PrejudiceStudioParser(BaseParser) :
    @property
    def group_name(self) -> str :
        return "Prejudice-Studio"

    @property
    def group_type(self) -> EnumGroupType :
        return EnumGroupType.Transfer

    def __init__(self) :
        super().__init__()
        self.language_map["简繁英"] = EnumLanguage.EngScTc

        self.single_episode_patterns = [
            re.compile(
                    r"\[Prejudice-Studio](?P<title>[^\[\]]+?)-\s?(?P<episode>\d+)(?:v(?P<version>\d+))?\s?\[(?P<websource>Bilibili)?\s?(?P<source>WEB-DL|WebRip)\s(?P<resolution>\d+p)\s(?P<codeV>AVC)\s(?P<videoRate>\d+bit)\s(?P<codeA>AAC)\s?(?P<extension>MP4|MKV)?]\[(?P<lang>.+?)]",
                    re.IGNORECASE
            ),
        ]
        self.multiple_episode_patterns = [
            re.compile(
                    r"\[Prejudice-Studio](?P<title>[^\[\]]+?)\s?\[(?P<start>\d+)-(?P<end>\d+)]\[(?P<websource>Bilibili)\s(?P<source>WEB-DL|WebRip)\s(?P<resolution>\d+p)\s(?P<codeV>AVC)\s(?P<videoRate>\d+bit)\s(?P<codeA>AAC)\s?(?P<extension>MP4|MKV)?]\[(?P<lang>.+?)]",
                    re.IGNORECASE
            ),
        ]

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
