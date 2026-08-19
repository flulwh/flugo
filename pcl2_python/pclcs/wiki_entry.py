"""
wiki_entry.py - MC 百科条目
翻译自：PCLCS/Resource/WikiEntry.cs
"""

import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from .constants import ResourcePlatforms


@dataclass
class WikiEntry:
    """
    MC 百科条目。
    
    使用 WikiEntry.all() 获取所有条目。
    """
    
    # 在 MC 百科中的对应 ID
    id: int = 0
    
    # 中文译名，None 代表没有翻译
    chinese_name: Optional[str] = None
    
    # 各个 Mod 平台的 Slug（例如 advanced-solar-panels）
    # 若没有对应键则为不在该平台上
    slugs: Dict[ResourcePlatforms, str] = field(default_factory=dict)
    
    # MC 百科的浏览量逆序排行，1 代表浏览量最低
    popularity: int = 0
    
    @classmethod
    def all(cls) -> List['WikiEntry']:
        """内置数据库中的所有 MC 百科条目。"""
        if not hasattr(cls, '_all_entries'):
            cls._all_entries = cls._load_entries()
        return cls._all_entries
    
    @staticmethod
    def _convert_radix_86_to_10(value: str) -> int:
        """
        将 86 进制字符串转换为 10 进制整数。
        C# 原代码使用自定义的 86 进制转换。
        字符集：0-9, A-Z, a-z, 以及一些特殊字符
        """
        # 86 进制字符集（根据 C# 代码推断）
        chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
        
        result = 0
        for char in value:
            if char not in chars:
                raise ValueError(f"无效的 86 进制字符：{char}")
            result = result * 86 + chars.index(char)
        return result
    
    @classmethod
    def _load_entries(cls) -> List['WikiEntry']:
        """加载并解析 WikiEntries.txt 文件。"""
        # 获取资源文件路径
        resource_dir = os.path.dirname(os.path.abspath(__file__))
        wiki_entries_path = os.path.join(resource_dir, 'WikiEntries.txt')
        
        if not os.path.exists(wiki_entries_path):
            # 如果文件不存在，返回空列表
            return []
        
        with open(wiki_entries_path, 'r', encoding='utf-8') as f:
            data_lines = [line.rstrip('\n') for line in f.readlines()]
        
        if not data_lines:
            return []
        
        # 读取最后一行的浏览量
        popularities = []
        last_line = data_lines[-1]
        for i in range(0, len(last_line), 3):  # 将每 3 个字符切割成一个元素
            if i + 3 <= len(last_line):
                segment = last_line[i:i+3]
                # 从 86 进制转换为 10 进制
                popularity = cls._convert_radix_86_to_10(segment)
                popularities.append(popularity)
        
        data_lines = data_lines[:-1]  # 移除最后一行
        
        # 解析每一行
        results = []
        line_number = 0
        
        for line_data in data_lines:
            line_number += 1
            if not line_data:
                continue
            
            popularity = popularities.pop(0) if popularities else 0
            
            # 按 ¨ 分割
            entry_data_list = line_data.split('¨')
            
            for entry_data in entry_data_list:
                entry = cls()
                parts = entry_data.split('|')
                slugs_str = parts[0]
                
                # 解析 Slugs
                if slugs_str.startswith('@'):
                    entry.slugs[ResourcePlatforms.Modrinth] = slugs_str.replace('@', '')
                elif slugs_str.endswith('@'):
                    curse_slug = slugs_str[:-1]
                    entry.slugs[ResourcePlatforms.CurseForge] = curse_slug
                    entry.slugs[ResourcePlatforms.Modrinth] = curse_slug
                elif '@' in slugs_str:
                    split_slugs = slugs_str.split('@')
                    entry.slugs[ResourcePlatforms.CurseForge] = split_slugs[0]
                    entry.slugs[ResourcePlatforms.Modrinth] = split_slugs[1]
                else:
                    entry.slugs[ResourcePlatforms.CurseForge] = slugs_str
                
                entry.id = line_number
                entry.popularity = popularity
                
                # 处理中文名称
                if len(parts) >= 2:
                    entry.chinese_name = parts[-1]  # 最后一项
                    if '*' in entry.chinese_name:
                        # 处理 * 占位符
                        english_name = list(entry.slugs.values())[0].replace('-', ' ').capitalize()
                        entry.chinese_name = entry.chinese_name.replace('*', f' ({english_name})')
                
                results.append(entry)
        
        return results
    
    def __str__(self) -> str:
        curse_slug = self.slugs.get(ResourcePlatforms.CurseForge, '')
        modrinth_slug = self.slugs.get(ResourcePlatforms.Modrinth, '')
        return f"{curse_slug}&{modrinth_slug}|{self.id}|{self.chinese_name}，浏览量 {self.popularity}"
