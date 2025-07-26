from enum import Enum


class EnumSubtitleType(Enum) :
    # 内嵌字幕
    Embedded = 1,
    # 内封字幕
    Muxed = 2,
    # 外挂字幕
    External = 3,
    # 无字幕
    Unknown = 4
