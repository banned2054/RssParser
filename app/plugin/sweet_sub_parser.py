import re

from app.models.enum.enum_group_type import EnumGroupType
from app.utils.parser.base_parser import BaseParser


class SweetSubParser(BaseParser) :
    @property
    def group_name(self) -> str :
        return "SweetSub"

    @property
    def group_type(self) -> EnumGroupType :
        return EnumGroupType.Translation

    def __init__(self) :
        super().__init__()
        self.single_episode_patterns = [
            re.compile(
                    r"\[SweetSub]\[(?P<title>[^\[\]]+?)]\[(?P<engTitle>[^\[\]]+?)]\[(?P<episode>\d+)(?:v(?P<version>\d+))?]\[(?P<source>[a-z]+Rip)]\[(?P<resolution>\d+p)]\[[^\[\]]*]\[(?P<lang>.+?)]",
                    re.IGNORECASE
            ),
            re.compile(
                    r"\[SweetSub](?P<title>[^\[\]]+?)-\s(?P<episode>\d+)(?:v(?P<version>\d+))?\s?\[(?P<source>[a-z]+Rip)]\[(?P<resolution>\d+p)]\[[^\[\]]*]\[(?P<lang>.+?)]",
                    re.IGNORECASE
            ),
        ]
        self.multiple_episode_patterns = [
            re.compile(
                    r"\[SweetSub]\[(?P<title>[^\[\]]+?)]\[(?P<engTitle>[^\[\]]+?)]\[(?P<start>\d+)-(?P<end>\d+)\s?(?P<OAD>[a-z一-鿿]+)?]\[(?P<source>[a-z]+Rip)]\[(?P<resolution>\d+p)]\[[^\[\]]*]\[(?P<lang>.+?)](\[v(?P<version1>\d+)])?",
                    re.IGNORECASE
            ),
        ]
