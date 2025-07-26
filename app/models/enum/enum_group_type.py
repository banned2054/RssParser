from enum import Enum


class EnumGroupType(Enum) :
    # 汉化组
    Translation = 1,
    # 搬运组
    Transfer = 2,
    # 压制组，例如vcb-studio
    Compression = 3
