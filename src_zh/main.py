# -*- coding: utf-8 -*-
import argparse
import sys
import os

# Ensure local imports work when frozen or run from source
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import file_text_searcher as core

def _parse_args():
    p = argparse.ArgumentParser(
        prog="text-searcher",
        description="跨目录文本搜索工具（支持命令行和GUI）"
    )
    p.add_argument("--gui", action="store_true", help="启动图形界面")
    p.add_argument("--interactive", action="store_true", help="启动交互式命令行菜单（默认行为）")

    p.add_argument("-s", "--search", help="要搜索的字符串（若未提供则进入交互模式）")
    p.add_argument("-b", "--batch", nargs="+", help="批量搜索多个字符串（以空格分隔）")
    p.add_argument("-d", "--dir", default="", help="要搜索的目录（留空=当前目录）")
    p.add_argument("-e", "--ext", action="append", help="文件通配符（可多次使用，例如 -e *.txt -e *.log）")
    p.add_argument("--all-types", action="store_true", help="使用常见文本类型（*.txt, *.log, *.csv, *.xml, *.json）")
    p.add_argument("-R", "--recursive", action="store_true", help="包含子目录")
    p.add_argument("-i", "--case-sensitive", action="store_true", help="区分大小写")

    return p.parse_args()

def main():
    args = _parse_args()

    if args.gui:
        import gui_app
        gui_app.launch()
        return

    # If neither search nor batch provided, or --interactive forced -> menu
    if args.interactive or (not args.search and not args.batch):
        core.menu_loop()
        return

    # Build file patterns
    if args.all_types:
        patterns = ["*.txt", "*.log", "*.csv", "*.xml", "*.json"]
    elif args.ext:
        patterns = args.ext
    else:
        patterns = ["*.txt"]

    if args.batch:
        for term in args.batch:
            print(f"\n>>> 搜索: '{term}'")
            for pat in patterns:
                core.search_in_files(term, pat, args.case_sensitive, args.dir, args.recursive)
    else:
        for pat in patterns:
            core.search_in_files(args.search, pat, args.case_sensitive, args.dir, args.recursive)

if __name__ == "__main__":
    main()
