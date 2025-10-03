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
        description="Cross-directory text search tool (supports command line and GUI)"
    )
    p.add_argument("--gui", action="store_true", help="Launch graphical interface")
    p.add_argument("--interactive", action="store_true", help="Launch interactive command line menu (default behavior)")

    p.add_argument("-s", "--search", help="String to search (if not provided, enter interactive mode)")
    p.add_argument("-b", "--batch", nargs="+", help="Batch search multiple strings (space separated)")
    p.add_argument("-d", "--dir", default="", help="Directory to search (blank=current directory)")
    p.add_argument("-e", "--ext", action="append", help="File wildcard (can be used multiple times, e.g. -e *.txt -e *.log)")
    p.add_argument("--all-types", action="store_true", help="Use common text types (*.txt, *.log, *.csv, *.xml, *.json)")
    p.add_argument("-R", "--recursive", action="store_true", help="Include subdirectories")
    p.add_argument("-i", "--case-sensitive", action="store_true", help="Case sensitive")

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
            print(f"\n>>> Searching: '{term}'")
            for pat in patterns:
                core.search_in_files(term, pat, args.case_sensitive, args.dir, args.recursive)
    else:
        for pat in patterns:
            core.search_in_files(args.search, pat, args.case_sensitive, args.dir, args.recursive)

if __name__ == "__main__":
    main()