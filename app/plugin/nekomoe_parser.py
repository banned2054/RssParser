# 在某个 parser 里或单独抽出一个 utils.py
import re

from app.models.enum.enum_group_type import EnumGroupType
from app.models.enum.enum_resolution import EnumResolution
from app.models.parser_result import ParseResult
from app.utils.parser.base_parser import BaseParser


class NekoMoeParser(BaseParser) :
    @property
    def group_name(self) -> str :
        return "Sakurato"

    @property
    def group_type(self) -> EnumGroupType :
        return EnumGroupType.Translation

    def __init__(self) :
        super().__init__()
        self.single_episode_patterns = [
            re.compile(
                    r"【(?:喵萌奶茶屋|喵萌Production)】(?:★\d+月新番★)?\[(?P<title>[^\[\]]+?)]\[(?P<episode>\d+)(?:v(?P<version>\d+))?](?:\[(?P<source>[a-z]+Rip)])?\[(?P<resolution>\d+p)]\[(?P<lang>.+?)]",
                    re.IGNORECASE
            ),
            re.compile(
                    r"【(?P<group>喵萌奶茶屋&[^\[\]]+)】(?:★\d+月新番★)?\[(?P<title>[^\[\]]+?)]\[(?P<episode>\d+)(?:v(?P<version>\d+))?](?:\[(?P<source>[a-z]+Rip)])?\[(?P<resolution>\d+p)]\[(?P<lang>.+?)]",
                    re.IGNORECASE
            ),
            re.compile(
                    r"\[Nekomoe kissaten]\[(?P<title>[^\[\]]+?)]\[(?P<episode>\d+)(?:v(?P<version>\d+))?](?:\[(?P<source>[a-z]+Rip)])?\[(?P<resolution>\d+p)]\[(?P<lang>.+?)]",
                    re.IGNORECASE
            ),
            re.compile(
                    r"\[(?P<group>[^\[\]]+&Nekomoe kissaten)]\[(?P<title>[^\[\]]+?)]\[(?P<episode>\d+)(?:v(?P<version>\d+))?](?:\[(?P<source>[a-z]+Rip)])?\[(?P<resolution>\d+p)]\[(?P<lang>.+?)]",
                    re.IGNORECASE
            ),
        ]
        self.multiple_episode_patterns = [
            re.compile(
                    r"【(?:喵萌奶茶屋|喵萌Production)】(?:★\d+月新番★)?\[(?P<title>[^\[\]]+?)]\[(?P<start>\d+)-(?P<end>\d+)(?:END)?(?:\+(?P<OAD>[a-z\u4e00-\u9fff]+))?](?:\[(?P<source>[a-z]+Rip)])?\[(?P<resolution>\d+p)]\[(?P<lang>.+?)]",
                    re.IGNORECASE
            ),
        ]

    def create_parsed_result_single(self, match: re.Match) -> ParseResult :
        episode_str = match.groupdict().get("episode", "0")
        episode = int(re.sub(r"\D+", "", episode_str)) if episode_str else None

        lang_str = match.groupdict().get("lang", "")
        resolution_str = match.groupdict().get("resolution", "")
        title = str(match.groupdict().get("title", "")).strip()

        lang, sub_type = self.detect_language_subtitle(lang_str)

        group = match.groupdict().get("lang", self.group_name)

        version_str = match.groupdict().get("version", '1')
        version = int(version_str) if version_str else 1

        return ParseResult(
                is_multiple = False,
                title = title,
                episode = episode,
                version = version,
                group = group,
                resolution = EnumResolution.from_string(resolution_str),
                language = lang,
                subtitle_type = sub_type,
        )
