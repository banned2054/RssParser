# parser_base.py
import abc
import re
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

    def __init__(self) :
        self.language_map = {}
        self.single_episode_patterns = []
        self.multiple_episode_patterns = []

    @property
    @abc.abstractmethod
    def group_name(self) -> str :
        """返回字幕组名称"""
        pass

    def try_match(self, filename: str) -> tuple[bool, ParsedInfo | None] :
        # 1) 尝试匹配单集格式
        for pattern in self.single_episode_patterns :
            match = pattern.match(filename)
            if match :
                return True, self._create_parsed_result_single(match)

        # 2) 尝试匹配多集格式
        for pattern in self.multiple_episode_patterns :
            match = pattern.match(filename)
            if match :
                return True, self._create_parsed_result_multiple(match)

        return False, None

    def _create_parsed_result_single(self, match: re.Match) -> ParsedInfo :
        episode_str = match.group("episode")
        episode = int(re.sub(r"\D+", "", episode_str)) if episode_str else -1

        language, subtitle_type = self._detect_language_subtitle(match.group("lang"))
        result = ParsedInfo(
                is_multiple = False,
                title = match.group("title").strip(),
                episode = episode,
                source_group = self.group_name,
                resolution = match.group("resolution"),
                language = language,
                subtitle_type = subtitle_type,
        )
        return result

    def _create_parsed_result_multiple(self, match: re.Match) -> ParsedInfo :
        start_str = match.group("start")
        end_str = match.group("end")

        start_episode = int(start_str) if start_str else -1
        end_episode = int(end_str) if end_str else -1

        language, subtitle_type = self._detect_language_subtitle(match.group("lang"))
        result = ParsedInfo(
                is_multiple = True,
                title = match.group("title").strip(),
                start_episode = start_episode,
                end_episode = end_episode,
                source_group = self.group_name,
                resolution = match.group("resolution"),
                language = language,
                subtitle_type = subtitle_type,
        )
        return result

    @abc.abstractmethod
    def _detect_language_subtitle(self, lang: str) -> tuple[str, str] :
        pass
