import re
from typing import Tuple

from app.models.enum.enum_group_type import EnumGroupType
from app.models.enum.enum_language import EnumLanguage
from app.models.enum.enum_subtitle_type import EnumSubtitleType
from app.utils.parser.base_parser import BaseParser


class SakuraHanaParser(BaseParser) :
    @property
    def group_name(self) -> str :
        return "樱桃花字幕组"

    @property
    def group_type(self) -> EnumGroupType :
        return EnumGroupType.Translation

    def __init__(self) :
        super().__init__()
        self.single_episode_patterns = [
            re.compile(
                    r"\[樱桃花字幕组](?P<title>[^\[\]]+?)-\s?(?P<episode>\d+)(?:v(?P<version>\d+))?\[(?P<resolution>\d+p)]\[[^\[\]]+]\[(?P<lang>.+?)]\[(?P<source>[a-z]+Rip)]",
                    re.IGNORECASE
            ),
            re.compile(
                    r"\[樱桃花字幕组](?P<title>[^\[\]]+?)-\s?(?P<episode>\d+)(?:v(?P<version>\d+))?\s?[(（]?(?P<resolution>\d+p)[)）]?\s*\[(?P<lang>.+?)]\s?\[[a-z0-9]+]",
                    re.IGNORECASE
            ),
            re.compile(
                    r"\[樱桃花字幕组](?P<title>[^\[\]]+?)-\s?(?P<episode>\d+)(?:v(?P<version>\d+))?\s?[(（]?(?P<resolution>\d+p)[)）]?\s?\[[a-z0-9]+]",
                    re.IGNORECASE
            ),
            re.compile(
                    r"\[樱桃花字幕组](?P<title>[^\[\]]+?)(])?\[(?P<episode>\d+)(?:v(?P<version>\d+))?]\[(?P<resolution>\d+p)(]\[)?\s?[^\[\]]+]\[(?P<lang>.+?)]",
                    re.IGNORECASE
            ),
            re.compile(
                    r"\[樱桃花字幕组](?P<title>[^\[\]]+?)-\s?(?P<episode>\d+)(?:v(?P<version>\d+))?\s?\[(?P<resolution>\d+p)]\[(?P<lang>.+?)]",
                    re.IGNORECASE
            ),
        ]
        self.multiple_episode_patterns = [
            re.compile(
                    r"\[樱桃花字幕组](?P<title>[^\[\]]+?)(])?\[(?P<start>\d+)-(?P<end>\d+)]\[(?P<resolution>\d+p)(]\[)?\s?[^\[\]]+]\[(?P<lang>.+?)]",
                    re.IGNORECASE
            ),
        ]

    def detect_language_subtitle(self, text: str) -> Tuple[EnumLanguage, EnumSubtitleType] :
        lower = text.lower().strip()
        lang = EnumLanguage.Unknown
        sub = EnumSubtitleType.Embedded

        for k, v in sorted(self.language_map.items(), key = lambda kv : len(kv[0]), reverse = True) :
            if k.lower() in lower :
                lang = v
                break

        return lang, sub
