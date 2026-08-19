"""
java.py - Java 相关功能
翻译自：PCLCS/Java.cs

注意：此模块依赖于 pclcs 的其他模块，部分功能可能需要进一步完善
"""

import os
import re
import asyncio
import threading
from pathlib import Path
from typing import List, Optional, Dict, Any, Set
from dataclasses import dataclass, field
from packaging.version import Version as PackagingVersion


@dataclass
class Java:
    """
    单个 Java 的实例。
    
    Args:
        folder: java.exe 文件所在的文件夹路径，这通常是 bin 文件夹
        version: Java 的版本号（例如 16.0.1）
    """
    
    def __init__(self, folder: str, version: Optional[PackagingVersion] = None):
        # java.exe 文件所在的文件夹路径，以 \\ 结尾
        self.folder = self._add_slash_suffix(self._path_for_compare(folder))
        
        # java.exe 文件的完整路径
        self.java_exe_path = os.path.join(self.folder, "java.exe")
        
        # Java 的版本号，若为 None 则还需要调用 check_async 以获取版本号
        self.version: Optional[PackagingVersion] = version
        
        # Java 的默认字符编码
        self.file_encoding_name: Optional[str] = None
        
        # Java 根据系统环境确定的本地字符编码，仅 Java 17+ 可用
        self.native_encoding_name: Optional[str] = None
        
        # 内部状态
        self._is_checked = 0
        self._available: Optional[bool] = None
    
    @staticmethod
    def _add_slash_suffix(path: str) -> str:
        """确保路径以分隔符结尾。"""
        if not path.endswith(os.sep):
            return path + os.sep
        return path
    
    @staticmethod
    def _path_for_compare(path: str) -> str:
        """标准化路径以便比较。"""
        # Windows 上转换为小写，Linux/Mac 保持原样
        if os.name == 'nt':
            return path.lower()
        return path
    
    async def check_async(self, cancellation_token: Optional[asyncio.Event] = None) -> bool:
        """
        检查该 Java 是否存在问题，并获取其版本号。
        
        Returns:
            是否通过了检查
        """
        # 检查是否已经检查过
        if threading.atomic.exchange(self, '_is_checked', 1) == 1 and self._available is not None:
            return self._available
        
        output = None
        try:
            if not os.path.exists(self.java_exe_path):
                raise FileNotFoundError(f"未找到 java.exe 文件：{self.java_exe_path}")
            
            # 运行 -version (简化版本，实际需要实现进程执行)
            # 这里需要调用 subprocess 来执行 java -version
            # 由于是翻译，保留逻辑结构，具体实现需要适配 Python
            output = await self._run_java_version_check()
            
            if output == "":
                raise RuntimeError("尝试运行该 Java 失败")
            
            # 日志记录（需要实现 Logger）
            print(f"Java 检查输出：{self.java_exe_path}\n{output}")
            
            if "/lib/ext exists" in output:
                raise RuntimeError("无法运行该 Java，请在删除 Java 文件夹中的 /lib/ext 文件夹后再试")
            
            if "a fatal error" in output or "error: " in output:
                raise RuntimeError("无法运行该 Java，该 Java 或系统存在问题")
            
            # 获取版本号
            version_match = re.search(r'(?<=version ")[^"]+', output)
            if not version_match:
                version_match = re.search(r'(?<=openjdk )[0-9]+', output)
            
            version_string = version_match.group(0) if version_match else None
            
            if not version_string:
                raise RuntimeError(f"未找到该 Java 的版本号")
            
            version_string = version_string.replace("_", ".").replace("+", ".")
            if "-" in version_string:
                version_string = version_string.split("-")[0]
            
            # 去除开头的 1.
            if version_string.startswith("1."):
                version_string = version_string[2:]
            
            segments = version_string.split(".")
            while len(segments) < 4:
                segments.append("0")
            
            version_str = ".".join(segments[:4])
            self.version = PackagingVersion(version_str)
            
            if self.version.major <= 4 or self.version.major >= 100:
                raise RuntimeError(f"分析详细信息失败，获取的版本为 {self.version}")
            
            # 获取 Java 的相关属性
            if "64-bit" not in output:
                raise RuntimeError("该 Java 为 32 位版本，请安装 64 位的 Java")
            
            # 获取编码属性
            def get_property(name: str) -> Optional[str]:
                prefix = f"{name} = "
                for line in output.split('\n'):
                    line = line.strip()
                    if line.startswith(prefix):
                        return line[len(prefix):].strip()
                return None
            
            self.file_encoding_name = get_property("file.encoding")
            self.native_encoding_name = get_property("native.encoding") or self.file_encoding_name
            
            print(f"检查 Java 成功：{self}")
            self._available = True
            
        except asyncio.CancelledError:
            self._is_checked = 0
            raise
        except Exception as ex:
            print(f"检查 Java 失败（{self.java_exe_path}），其输出为：\n{output or '无程序输出'}")
            self._available = False
        
        return self._available
    
    async def _run_java_version_check(self) -> str:
        """运行 Java 版本检查命令。"""
        # 这是一个占位实现，实际需要调用 subprocess
        # 由于跨平台差异和异步需求，这里需要进一步完善
        try:
            proc = await asyncio.create_subprocess_exec(
                self.java_exe_path,
                "-XshowSettings:properties",
                "-version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT
            )
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=15)
            return stdout.decode('utf-8', errors='ignore').lower()
        except Exception:
            return ""
    
    def invalidate_checked(self):
        """使已检查的状态失效。"""
        self._is_checked = 0
        self._available = None
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Java):
            return False
        return self.folder.lower() == other.folder.lower()
    
    def __hash__(self) -> int:
        return hash(self.folder.lower())
    
    def __str__(self) -> str:
        version_str = str(self.version.major) if self.version else "尚未检查"
        return f"Java {version_str} ({self.version})：{self.folder}"


class JavaUtils:
    """Java 工具类。"""
    
    # 存在完整 Java 的文件夹列表（懒加载）
    _candidate_folders: Optional[List[str]] = None
    
    @classmethod
    def candidate_folders(cls) -> List[str]:
        """获取候选 Java 文件夹列表。"""
        if cls._candidate_folders is None:
            cls._candidate_folders = cls._init_candidate_folders()
        return cls._candidate_folders
    
    @staticmethod
    def _init_candidate_folders() -> List[str]:
        """初始化候选 Java 文件夹列表。"""
        app_data = os.environ.get('APPDATA', '')
        user_profile = os.environ.get('USERPROFILE', '')
        local_app_data = os.environ.get('LOCALAPPDATA', '')
        program_files_x86 = os.environ.get('PROGRAMFILES(X86)', '')
        program_files = os.environ.get('PROGRAMFILES', '')
        my_documents = os.environ.get('USERPROFILE', '') + '\\Documents'
        
        folders = [
            app_data + r'\.minecraft\runtime\',
            app_data + r'\.hmcl\java\',
            app_data + r'\ATLauncher\runtimes\minecraft\',
            app_data + r'\ModrinthApp\meta\java_versions\',
            app_data + r'\PrismLauncher\java\',
            user_profile + r'\curseforge\minecraft\Install\runtime\',
            user_profile + r'\.jdks\',
            user_profile + r'\.sdkman\candidates\java\',
            local_app_data + r'\.ftba\bin\runtime\',
            local_app_data + r'\Packages\Microsoft.4297127D64EC6_8wekyb3d8bbwe\LocalCache\Local\runtime\',
            program_files_x86 + r'\Minecraft Launcher\runtime\',
            program_files_x86 + r'\Minecraft\runtime\',
            my_documents + r'\Curse\Minecraft\Install\runtime\',
            program_files + r'\Java\',
            program_files + r'\Eclipse Adoptium\',
            program_files + r'\Amazon Corretto\',
            program_files + r'\Zulu\',
        ]
        
        # 添加环境变量中的路径
        jdk_home = os.environ.get('JDK_HOME', '')
        java_home = os.environ.get('JAVA_HOME', '')
        env_paths = [p.strip().strip('"') for p in (jdk_home + ';' + java_home).split(';') if p.strip()]
        folders.extend(env_paths)
        
        # 过滤无效路径
        valid_folders = []
        for f in folders:
            try:
                valid_folders.append(Java._path_for_compare(f))
            except Exception:
                print(f"Java 候选文件夹路径无效（{f}）")
        
        return valid_folders
    
    @classmethod
    async def check_all_async(cls, javas: List[Java], 
                              cancellation_token: Optional[asyncio.Event] = None,
                              progress: Optional[Any] = None) -> List[Java]:
        """
        检查所有指定的 Java 是否存在问题，并获取其版本号。
        
        Returns:
            所有通过检查的 Java
        """
        unchecked_javas = [j for j in javas if j._available is None]
        
        tasks = [java.check_async(cancellation_token) for java in unchecked_javas]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        return [j for j in javas if j._available is True]
    
    @classmethod
    async def sort_async(cls, javas: List[Java],
                        cancellation_token: Optional[asyncio.Event] = None,
                        progress: Optional[Any] = None) -> List[Java]:
        """
        将 Java 列表进行排序。
        这同时会检查所有未检查的 Java。
        """
        javas = await cls.check_all_async(javas, cancellation_token, progress)
        
        def sort_key(java: Java) -> tuple:
            # 优先使用带完整 Java 的文件夹列表中的 Java
            is_in_candidate = any(
                cls._is_parent_of(folder, java.folder) 
                for folder in cls.candidate_folders()
            )
            
            # 其次优先使用主版本号接近 21 的 Java
            if java.version:
                distance = abs(java.version.major - 21)
            else:
                distance = float('inf')
            
            return (not is_in_candidate, distance)
        
        javas.sort(key=sort_key)
        return javas
    
    @staticmethod
    def _is_parent_of(parent: str, child: str) -> bool:
        """检查 parent 是否是 child 的父目录。"""
        parent = parent.rstrip(os.sep) + os.sep
        child = child.rstrip(os.sep) + os.sep
        return child.startswith(parent)
    
    @classmethod
    async def refresh_list_async(cls, cancellation_token: Optional[asyncio.Event] = None,
                                 progress: Optional[Any] = None):
        """从常见文件夹和环境变量中搜索 Java，并将搜索结果写入设置。"""
        # 搜索
        java_list = await cls.search_folders_async(
            include_sub_directories=True,
            folders=cls.candidate_folders(),
            cancellation_token=cancellation_token,
            progress=progress.split_to(0.5) if progress else None
        )
        
        # TODO: 这里需要集成配置系统
        # old_java_list = Configs.JavaList.get()
        old_java_list = []
        
        # 检查原有列表中的 Java
        old_java_list = await cls.check_all_async(old_java_list, cancellation_token, 
                                                   progress.split_to(0.9) if progress else None)
        
        # 移除已存在的 Java
        java_list = [j for j in java_list if j not in old_java_list]
        
        # 排序并合并
        java_list = await cls.sort_async(java_list, cancellation_token)
        java_list.extend(old_java_list)
        
        # 去重
        java_list = list(dict.fromkeys(java_list))
        
        # TODO: 删掉已被移除的 Java
        # java_list.remove_if(j => Configs.JavaRemovedList.get()!.Contains(j.Folder, ...))
        
        # TODO: 写入设置
        # Configs.JavaList.set(java_list)
        
        print(f"Java 搜索完成，发现 {len(java_list)} 个 Java")
        return java_list
    
    @classmethod
    async def search_folders_async(cls, include_sub_directories: bool,
                                   folders: List[str],
                                   cancellation_token: Optional[asyncio.Event] = None,
                                   progress: Optional[Any] = None) -> List[Java]:
        """
        并行搜索所有指定的文件夹及其子文件夹中的 Java，并检查其有效性。
        """
        results: Set[str] = set()
        
        async def search_folder(folder: str):
            try:
                search_pattern = "**/java.exe" if include_sub_directories else "java.exe"
                for root, dirs, files in os.walk(folder):
                    if "java.exe" in files:
                        target_folder = cls._add_slash_suffix(
                            cls._path_for_compare(os.path.dirname(os.path.join(root, "java.exe")))
                        )
                        
                        # 检查重解析点和特殊路径（简化版本）
                        has_reparse_point = False
                        is_special_path = any(x in target_folder for x in [
                            "java8path_target_", "javapath_target_", "javatmp", "system32"
                        ])
                        
                        if not has_reparse_point and not is_special_path:
                            results.add(target_folder)
                    
                    if not include_sub_directories:
                        break
            except PermissionError:
                print(f"快速查找 Java 时没有权限（{folder}）")
            except Exception as ex:
                print(f"快速查找 Java 时出错（{folder}）: {ex}")
        
        # 并发搜索
        tasks = [search_folder(folder) for folder in set(folders)]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        if not results:
            return []
        
        # 创建 Java 对象并检查
        java_list = [Java(folder) for folder in results]
        java_list = await cls.check_all_async(java_list, cancellation_token, 
                                               progress.split_to(1) if progress else None)
        java_list = await cls.sort_async(java_list, cancellation_token)
        
        print(f"快速查找 Java 完成，共有 {len(java_list)} 个候选")
        return java_list
