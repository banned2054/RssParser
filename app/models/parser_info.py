# parser_base.py
import abc
from dataclasses import dataclass
from typing import Optional


@dataclass
class ParsedInfo :
    is_multiple: bool = False
    title: str = ""
    episode: Optional[int] = None
    start_episode: Optional[int] = None
    end_episode: Optional[int] = None
    source_group: str = ""
    language: str = ""
    subtitle_type: str = ""
    resolution: str = ""
    season: int = 1
    source: str = "WebRip"


class IMatchingStrategy(abc.ABC) :
    """抽象基类，所有字幕组的解析策略都要继承它。"""

    @property
    @abc.abstractmethod
    def group_name(self) -> str :
        """返回字幕组名称"""
        pass

    @abc.abstractmethod
    def try_match(self, filename: str) -> tuple[bool, Optional[ParsedInfo]] :
        """
        尝试匹配 `filename`，若成功解析则返回 (True, ParsedResult)，否则返回 (False, None)
        """
        pass
