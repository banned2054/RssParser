import re
from enum import Enum


class EnumResolution(Enum) :
    R480p = 1
    R720p = 2
    R1080p = 3
    R2K = 4
    R4K = 5
    Unknown = 6

    @staticmethod
    def from_string(resolution: str) -> "EnumResolution" :
        resolution = resolution.strip()

        # 匹配分辨率，如 1920x1080 或 3840×2160
        match = re.match(r"(?P<width>\d+)[x×X*](?P<height>\d+)", resolution, re.IGNORECASE)
        if match :
            width = int(match.group("width"))
            height = int(match.group("height"))
            if height >= 2160 :
                return EnumResolution.R4K
            elif height >= 1080 and width >= 2048 :
                return EnumResolution.R2K
            elif height >= 1080 :
                return EnumResolution.R1080p
            elif height >= 720 :
                return EnumResolution.R720p
            elif height >= 480 :
                return EnumResolution.R480p
            else :
                return EnumResolution.Unknown

        # 匹配720p, 1080p, 2160p 等
        match = re.match(r"(?P<height>\d{3,4})p", resolution.lower())
        if match :
            height = int(match.group("height"))
            if height < 600 :
                return EnumResolution.R480p
            elif height < 900 :
                return EnumResolution.R720p
            elif height < 1260 :
                return EnumResolution.R1080p
            elif height < 1800 :
                return EnumResolution.R2K
            else :
                return EnumResolution.R4K

        return EnumResolution.Unknown
