from enum import Enum


class EnumLanguage(Enum) :
    # 简体日语
    JpSc = 1,
    # 简繁双语
    ScTc = 2,
    # 简日繁三语
    JpScTc = 3,
    # 简体
    Sc = 4,
    # 繁体日语
    JpTc = 5,
    # 繁体
    Tc = 6,
    # 日语
    Jp = 7,
    # 无字幕
    Unknown = 8,
    # 英语
    Eng = 9,
    # 简体英语
    EngSc = 10,
    # 繁体英语
    EngTc = 11,
    # 简英繁三语
    EngScTc = 12
