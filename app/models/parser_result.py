from dataclasses import dataclass
from typing import Optional

from app.models.enum.enum_group_type import EnumGroupType
from app.models.enum.enum_language import EnumLanguage
from app.models.enum.enum_resolution import EnumResolution
from app.models.enum.enum_subtitle_type import EnumSubtitleType


@dataclass
class ParseResult :
    # 是多集还是单集
    is_multiple: bool = False

    # 解析后的纯标题，可能多语言
    title: str = ""

    # 单集集数
    episode: Optional[float] = None
    # 单集版本
    version: Optional[int] = None

    # 多集的第一集
    start_episode: Optional[int] = None

    # 多集的最后一集
    end_episode: Optional[int] = None

    # 字幕组、压制组或者搬运组
    group: str = ""

    # 字幕组、压制组还是搬运组
    group_type: EnumGroupType = EnumGroupType.Translation

    # 字幕语言
    language: EnumLanguage = EnumLanguage.Unknown

    # 字幕类型
    subtitle_type: EnumSubtitleType = EnumSubtitleType.Unknown

    # 分辨率
    resolution: EnumResolution = EnumResolution.Unknown

    # 季度
    season: int = 1

    # 来源，WebRip、BDRip或者BDMV
    source: str = "WebRip"

    # 搬运组专用，搬运组的源
    web_source: str = ""
