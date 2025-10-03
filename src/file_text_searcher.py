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
        print(f"No files matching {file_extension} found in directory '{directory}'")
        return 0

    print(f"Searching {len(files)} files in directory '{directory}', keyword: '{search_string}'\n")

    found_files = 0
    for file_path in files:
        try:
            first = True
            for line_num, line in iter_matches(file_path, search_string, case_sensitive):
                if first:
                    print(f"🔍 Match found: {file_path}")
                    first = False
                    found_files += 1
                print(f"   Line {line_num}: {line.strip()}")
            if not first:
                print("-" * 50)
        except Exception as e:
            print(f"❌ Failed to process file '{file_path}': {e}")

    print(f"\nSearch completed! Found '{search_string}' in {found_files} files")
    return found_files

# ------------------ Interactive CLI (preserved & improved) ------------------

def _prompt_directory() -> str:
    d = input("Enter directory to search (blank=current directory): ").strip()
    return d

def _prompt_recursive() -> bool:
    return input("Include subdirectories? (y/N): ").strip().lower() == "y"

def search_with_options():
    """
    Provide interactive search options (single search)
    """
    print("=== Text Search Tool (Single Search) ===")

    search_string = input("Enter string to search: ").strip()
    if not search_string:
        print("Search string cannot be empty!")
        return

    # Directory
    directory = _prompt_directory()
    recursive = _prompt_recursive()

    print("\nPlease select file type:")
    print("1. .txt files")
    print("2. .log files")
    print("3. .csv files")
    print("4. .xml files")
    print("5. .json files")
    print("6. Common text types (*.txt, *.log, *.csv, *.xml, *.json)")
    print("7. Custom wildcard (e.g. *.py, *.md)")

    choice = input("Please choose (1-7): ").strip()

    file_extensions = {
        "1": "*.txt",
        "2": "*.log",
        "3": "*.csv",
        "4": "*.xml",
        "5": "*.json",
        "6": ["*.txt", "*.log", "*.csv", "*.xml", "*.json"]
    }

    if choice == "7":
        custom_ext = input("Enter file wildcard (e.g. *.py, *.md): ").strip()
        file_extension = custom_ext or "*.txt"
    elif choice in file_extensions:
        file_extension = file_extensions[choice]
    else:
        print("Invalid input, using *.txt by default")
        file_extension = "*.txt"

    case_sensitive = input("Case sensitive? (y/N): ").strip().lower() == "y"

    print("\nStarting search...")
    if isinstance(file_extension, list):
        for ext in file_extension:
            search_in_files(search_string, ext, case_sensitive, directory, recursive)
    else:
        search_in_files(search_string, file_extension, case_sensitive, directory, recursive)

def batch_search():
    """
    Batch search for multiple strings
    """
    print("=== Batch Search Mode ===")
    print("Enter multiple search strings (separated by commas):")
    search_strings_input = input().strip()

    if not search_strings_input:
        print("Search strings cannot be empty!")
        return

    search_strings = [s.strip() for s in search_strings_input.split(",") if s.strip()]

    directory = _prompt_directory()
    recursive = _prompt_recursive()

    file_extension = input("Enter file wildcard (default: *.txt): ").strip() or "*.txt"
    case_sensitive = input("Case sensitive? (y/N): ").strip().lower() == "y"

    for search_string in search_strings:
        print(f"\nSearching: '{search_string}'")
        search_in_files(search_string, file_extension, case_sensitive, directory, recursive)

def menu_loop():
    """
    Top-level interactive loop (preserves original menu experience)
    """
    while True:
        print("\n" + "=" * 50)
        print("Text Search Tool")
        print("=" * 50)
        print("1. Single Search")
        print("2. Batch Search Multiple Strings")
        print("3. Exit")

        choice = input("Select mode (1-3): ").strip()

        if choice == "1":
            search_with_options()
        elif choice == "2":
            batch_search()
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice, please try again!")

if __name__ == "__main__":
    # Running this file directly preserves the interactive CLI
    menu_loop()
