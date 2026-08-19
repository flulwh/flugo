"""
constants.py - 常量和枚举定义
翻译自：PCLCS/Constants.cs
"""

from enum import IntFlag, IntEnum
from typing import Final


class ResourceTypes(IntFlag):
    """社区资源的类型。"""
    Mod = 1  # Mod
    ModPack = 2  # 整合包
    ResourcePack = 4  # 资源包
    Shader = 8  # 光影包
    DataPack = 16  # 数据包
    Plugin = 32  # 服务端插件
    Map = 64  # 地图
    ModOrDataPack = Mod | DataPack  # 同时包含数据包以及 Mod
    Any = Mod | ModPack | ResourcePack | Shader | DataPack | Plugin | Map  # 允许任意种类，或种类未知


class ResourcePlatforms(IntFlag):
    """社区资源的来源平台。"""
    CurseForge = 1
    Modrinth = 2
    Any = CurseForge | Modrinth


class ModLoaders(IntFlag):
    """Mod 加载器的类型。"""
    None_ = 0
    Forge = 1
    LiteLoader = 2
    Fabric = 4
    NeoForge = 16
    All = Forge | LiteLoader | Fabric | NeoForge


class DonationRank(IntEnum):
    """在爱发电中的赞助等级。"""
    None_ = 0
    Rank6 = 6
    Rank12 = 12
    Rank23 = 23
    Rank54 = 54
    Rank98 = 98


class Versions:
    """版本号常量类。"""
    # 土豆码版本号
    PotatoVersion: Final[str] = '1'
    # 版本管理中 Mod 信息缓存的版本号
    LocalModCacheVersion: Final[int] = 19
    # Minecraft 本地实例信息缓存的版本号
    McInstanceCacheVersion: Final[int] = 38
    # Java 相关配置的版本号
    JavaConfigVersion: Final[int] = 1
