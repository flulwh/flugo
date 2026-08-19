# PCL2 Python 版本

这是基于 [Meloong-Git/PCL](https://github.com/Meloong-Git/PCL) 项目翻译的 Python 版本。

## 项目说明

PCL (Plain Craft Launcher 2) 原本是一个使用 C#/VB.NET 编写的 Minecraft 启动器。本项目旨在将其核心功能逐行翻译成 Python 语言。

## 当前进度

### 已完成的模块 (PCLCS 核心服务)

- ✅ `constants.py` - 常量和枚举定义
  - ResourceTypes (资源类型)
  - ResourcePlatforms (资源平台)
  - ModLoaders (Mod 加载器)
  - DonationRank (赞助等级)
  - Versions (版本号常量)

- ✅ `resource.py` - 资源相关功能
  - CurseForge ModLoaderType 映射

- ✅ `wiki_entry.py` - MC 百科条目
  - WikiEntry 类
  - 条目加载和解析

- ✅ `java.py` - Java 相关功能
  - Java 类（Java 实例管理）
  - JavaUtils 工具类
  - Java 搜索和验证

### 待完成的模块

- ⏳ LaunchUtils - 启动工具
- ⏳ Configs - 配置系统
- ⏳ 主启动器界面 (WPF -> PyQt/Tkinter)
- ⏳ 各个页面模块
- ⏳ 控件库
- ⏳ 其他业务逻辑模块

## 安装

```bash
pip install -r requirements.txt
```

## 使用示例

```python
from pclcs import constants, resource, wiki_entry, java

# 使用常量
print(constants.ResourceTypes.Mod)
print(constants.ModLoaders.Forge)

# 资源映射
loader_type = resource.from_curseforge_mod_loader_type(1)
print(loader_type)  # ModLoaders.Forge

# MC 百科条目
entries = wiki_entry.WikiEntry.all()
if entries:
    print(f"共有 {len(entries)} 个百科条目")
    print(entries[0])

# Java 管理 (需要异步)
import asyncio

async def check_java():
    java_instance = java.Java(r"C:\Program Files\Java\jdk-17\bin")
    is_valid = await java_instance.check_async()
    print(f"Java 检查：{is_valid}")
    print(java_instance)

# asyncio.run(check_java())
```

## 注意事项

1. **跨平台兼容性**: 原项目主要针对 Windows，Python 版本正在适配跨平台
2. **异步支持**: 使用 asyncio 实现原项目的异步功能
3. **依赖项**: 部分 .NET 特有功能需要寻找 Python 等价实现
4. **UI 框架**: 原 WPF 界面需要迁移到 PyQt6 或 Tkinter

## 项目结构

```
pcl2_python/
├── pclcs/                  # PCL 社区服务核心
│   ├── __init__.py
│   ├── constants.py        # 常量定义
│   ├── resource.py         # 资源处理
│   ├── wiki_entry.py       # 百科条目
│   ├── java.py            # Java 管理
│   └── WikiEntries.txt    # 百科数据
├── requirements.txt
└── README.md
```

## 许可证

遵循原项目的 LICENSE

## 贡献

欢迎提交 Issue 和 Pull Request！
