# sakurato_parser.py
import re

from app.models.enum.enum_group_type import EnumGroupType
from app.utils.parser.base_parser import BaseParser


class SakuratoParser(BaseParser) :
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
                    r"\[[樱桜]都字幕[組组]](?P<title>[^\[\]]+?)\[(?P<episode>\d+)(?:v(?P<version>\d+))?]\[(?P<resolution>\d+p)]\[(?P<lang>.+?)]",
                    re.IGNORECASE
            ),
            re.compile(
                    r"\[Sakurato](?P<title>[^\[\]]+?)\[(?P<episode>\d+)(?:v(?P<version>\d+))?]\[(?P<vcodec>(HEVC|AVC|AVC-8bit|HEVC-10bit))?\s?(?P<resolution>\d+p)\s?(?P<acodec>(AAC))?]\[(?P<lang>.+?)]",
                    re.IGNORECASE
            ),
            re.compile(
                    r"\[[樱桜]都字幕[組组]](?P<title>[^\[\]]+?)\[(?P<resolution>\d+p)]\[(?P<lang>.+?)]",
                    re.IGNORECASE
            ),
            re.compile(
                    r"\[Sakurato](?P<title>[^\[\]]+?)\[(?P<resolution>\d+p)]\[(?P<lang>.+?)]",
                    re.IGNORECASE
            ),
        ]
        self.multiple_episode_patterns = [
            re.compile(
                    r"\[[樱桜]都字幕[組组]](?P<title>[^\[\]]+?)\[(?P<start>\d+)-(?P<end>\d+)(?:END)?(?:\+(?P<OAD>[a-z\u4e00-\u9fff]+))?]\[(?P<resolution>\d+p)]\[(?P<lang>.+?)]",
                    re.IGNORECASE
            ),
        ]
