# -*- coding: utf-8 -*-
"""
Enhanced text searcher: supports specifying directory (blank -> current dir),
optional recursive search, and preserves interactive CLI mode.

This file is adapted from the user's original script.
"""
import os
import glob
from typing import Iterable, List, Tuple, Generator, Union

def _normalize_dir(directory: str) -> str:
    d = directory or os.getcwd()
    return os.path.abspath(d)

def iter_files(directory: str, file_patterns: Union[str, List[str]], recursive: bool=False) -> List[str]:
    """
    Return a de-duplicated list of files in 'directory' matching the given glob pattern(s).
    If recursive is True, includes subdirectories.
    """
    directory = _normalize_dir(directory)
    patterns = [file_patterns] if isinstance(file_patterns, str) else list(file_patterns)

    files = []
    for pattern in patterns:
        if recursive:
            glob_pattern = os.path.join(directory, "**", pattern)
            files.extend(glob.glob(glob_pattern, recursive=True))
        else:
            glob_pattern = os.path.join(directory, pattern)
            files.extend(glob.glob(glob_pattern))

    # keep unique existing files only
    seen = set()
    uniq = []
    for p in files:
        if os.path.isfile(p) and p not in seen:
            uniq.append(p)
            seen.add(p)
    return uniq

def iter_matches(file_path: str, search_string: str, case_sensitive: bool=False) -> Generator[Tuple[int, str], None, None]:
    """
    Yield (line_number, line_text) for each matching line in file_path.
    Tries utf-8 first, then falls back to gbk and latin-1.
    """
    needle = search_string if case_sensitive else search_string.lower()

    def _scan(handle):
        for i, line in enumerate(handle, 1):
            hay = line if case_sensitive else line.lower()
            if needle in hay:
                yield i, line.rstrip("\n")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            yield from _scan(f)
        return
    except UnicodeDecodeError:
        pass
    except Exception as e:
        # Re-raise to let caller handle
        raise

    # encodings fallbacks
    for enc in ("gbk", "latin-1"):
        try:
            with open(file_path, "r", encoding=enc, errors="ignore") as f:
                yield from _scan(f)
            return
        except Exception:
            continue

def search_in_files(search_string: str,
                    file_extension: Union[str, List[str]]="*.txt",
                    case_sensitive: bool=False,
                    directory: str="",
                    recursive: bool=False) -> int:
    """
    Search for 'search_string' under 'directory' (blank -> current dir).
    Returns the number of files that contain at least one match.
    """
    directory = _normalize_dir(directory)
    files = iter_files(directory, file_extension, recursive=recursive)

    if not files:
        print(f"在目录 '{directory}' 中未找到匹配 {file_extension} 的文件")
        return 0

    print(f"在目录 '{directory}' 中搜索 {len(files)} 个文件，关键字：'{search_string}'\n")

    found_files = 0
    for file_path in files:
        try:
            first = True
            for line_num, line in iter_matches(file_path, search_string, case_sensitive):
                if first:
                    print(f"🔍 命中：{file_path}")
                    first = False
                    found_files += 1
                print(f"   行 {line_num}: {line.strip()}")
            if not first:
                print("-" * 50)
        except Exception as e:
            print(f"❌ 处理文件失败 '{file_path}': {e}")

    print(f"\n搜索完成！在 {found_files} 个文件中发现 '{search_string}'")
    return found_files

# ------------------ Interactive CLI (preserved & improved) ------------------

def _prompt_directory() -> str:
    d = input("输入要搜索的目录（留空=当前目录）: ").strip()
    return d

def _prompt_recursive() -> bool:
    return input("包含子目录? (y/N): ").strip().lower() == "y"

def search_with_options():
    """
    Provide interactive search options (single search)
    """
    print("=== 文本搜索工具（单次搜索） ===")

    search_string = input("输入要搜索的字符串: ").strip()
    if not search_string:
        print("搜索字符串不能为空！")
        return

    # Directory
    directory = _prompt_directory()
    recursive = _prompt_recursive()

    print("\n请选择文件类型:")
    print("1. .txt 文件")
    print("2. .log 文件")
    print("3. .csv 文件")
    print("4. .xml 文件")
    print("5. .json 文件")
    print("6. 常见文本类型 (*.txt, *.log, *.csv, *.xml, *.json)")
    print("7. 自定义通配符（例如 *.py, *.md）")

    choice = input("请选择 (1-7): ").strip()

    file_extensions = {
        "1": "*.txt",
        "2": "*.log",
        "3": "*.csv",
        "4": "*.xml",
        "5": "*.json",
        "6": ["*.txt", "*.log", "*.csv", "*.xml", "*.json"]
    }

    if choice == "7":
        custom_ext = input("输入文件通配符（例如 *.py, *.md）: ").strip()
        file_extension = custom_ext or "*.txt"
    elif choice in file_extensions:
        file_extension = file_extensions[choice]
    else:
        print("输入无效，默认使用 *.txt")
        file_extension = "*.txt"

    case_sensitive = input("区分大小写? (y/N): ").strip().lower() == "y"

    print("\n开始搜索...")
    if isinstance(file_extension, list):
        for ext in file_extension:
            search_in_files(search_string, ext, case_sensitive, directory, recursive)
    else:
        search_in_files(search_string, file_extension, case_sensitive, directory, recursive)

def batch_search():
    """
    Batch search for multiple strings
    """
    print("=== 批量搜索模式 ===")
    print("输入多个要搜索的字符串（以英文逗号分隔）:")
    search_strings_input = input().strip()

    if not search_strings_input:
        print("搜索字符串不能为空！")
        return

    search_strings = [s.strip() for s in search_strings_input.split(",") if s.strip()]

    directory = _prompt_directory()
    recursive = _prompt_recursive()

    file_extension = input("输入文件通配符（默认: *.txt）: ").strip() or "*.txt"
    case_sensitive = input("区分大小写? (y/N): ").strip().lower() == "y"

    for search_string in search_strings:
        print(f"\n正在搜索: '{search_string}'")
        search_in_files(search_string, file_extension, case_sensitive, directory, recursive)

def menu_loop():
    """
    Top-level interactive loop (preserves original menu experience)
    """
    while True:
        print("\n" + "=" * 50)
        print("文本搜索工具")
        print("=" * 50)
        print("1. 单次搜索")
        print("2. 批量搜索多个字符串")
        print("3. 退出")

        choice = input("选择模式 (1-3): ").strip()

        if choice == "1":
            search_with_options()
        elif choice == "2":
            batch_search()
        elif choice == "3":
            print("再见!")
            break
        else:
            print("无效选择，请重试！")

if __name__ == "__main__":
    # Running this file directly preserves the interactive CLI
    menu_loop()
