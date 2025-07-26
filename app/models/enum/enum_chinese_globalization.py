from enum import Enum


class EnumChineseGlobalization(Enum) :
    # 不修改繁体简体
    NotChange = 1
    # 全都切换成简体
    Simplified = 2
    # 全都切换成繁体
    Traditional = 3
