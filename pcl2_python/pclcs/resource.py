"""
resource.py - 资源相关功能
翻译自：PCLCS/Resource/Resource.cs
"""

from typing import Union
from enum import IntFlag
from .constants import ModLoaders


def from_curseforge_mod_loader_type(mod_loader_type: int) -> ModLoaders:
    """
    将 CurseForge 的 ModLoaderType 映射为 ModLoaders 枚举。
    
    参考：https://docs.curseforge.com/rest-api/#tocS_ModLoaderType
    """
    match mod_loader_type:
        case 1:
            return ModLoaders.Forge
        case 3:
            return ModLoaders.LiteLoader
        case 4:
            return ModLoaders.Fabric
        case 6:
            return ModLoaders.NeoForge
        case _:
            return ModLoaders.None_


def to_curseforge_mod_loader_type(loaders: ModLoaders) -> int:
    """
    将 ModLoaders 映射为 CurseForge 的单一 ModLoaderType。
    
    Args:
        loaders: ModLoaders 枚举值
        
    Returns:
        CurseForge 的 ModLoaderType 整数值
        
    Raises:
        ValueError: 当传入的枚举值不是单个 Mod Loader 时
    """
    if loaders == ModLoaders.None_:
        return 0
    
    # 检查是否为单个标志位
    if not _is_single_flag(loaders):
        raise ValueError(f"传入的枚举值 {loaders} 并非单个 Mod Loader")
    
    match loaders:
        case ModLoaders.Forge:
            return 1
        case ModLoaders.LiteLoader:
            return 3
        case ModLoaders.Fabric:
            return 4
        case ModLoaders.NeoForge:
            return 6
        case _:
            return 0


def _is_single_flag(value: IntFlag) -> bool:
    """检查 IntFlag 是否只设置了单个标志位。"""
    return value != 0 and (value & (value - 1)) == 0
