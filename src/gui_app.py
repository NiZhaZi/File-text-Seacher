# -*- coding: utf-8 -*-
import os
import sys
import threading
import queue
import csv
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Local core import
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import file_text_searcher as core

def _open_in_os(path: str):
    try:
        if sys.platform.startswith("win"):
            os.startfile(path)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            import subprocess
            subprocess.call(["open", path])
        else:
            import subprocess
            subprocess.call(["xdg-open", path])
    except Exception as e:
        messagebox.showerror("Open Failed", f"Cannot open file: {e}")

class SearchApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Text Search Tool (GUI)")
        self.geometry("1000x640")
        self.minsize(860, 520)

        self._build_vars()
        self._build_ui()

        self.worker = None
        self.q = queue.Queue()
        self.after(100, self._drain_queue)

    def _build_vars(self):
        self.var_dir = tk.StringVar(value=os.getcwd())
        self.var_search = tk.StringVar()
        self.var_case = tk.BooleanVar(value=False)
        self.var_recursive = tk.BooleanVar(value=False)

        # file type checkboxes
        self.var_txt = tk.BooleanVar(value=True)
        self.var_log = tk.BooleanVar(value=False)
        self.var_csv = tk.BooleanVar(value=False)
        self.var_xml = tk.BooleanVar(value=False)
        self.var_json = tk.BooleanVar(value=False)
        self.var_custom = tk.StringVar(value="")

        self.total_files = 0
        self.matched_files = 0
        self.total_hits = 0

    def _build_ui(self):
        pad = {"padx": 8, "pady": 6}

        frm_top = ttk.Frame(self)
        frm_top.pack(fill="x")

        ttk.Label(frm_top, text="Search term:").grid(row=0, column=0, sticky="w", **pad)
        ttk.Entry(frm_top, textvariable=self.var_search, width=42).grid(row=0, column=1, sticky="we", **pad)

        ttk.Label(frm_top, text="Directory:").grid(row=0, column=2, sticky="w", **pad)
        e_dir = ttk.Entry(frm_top, textvariable=self.var_dir, width=40)
        e_dir.grid(row=0, column=3, sticky="we", **pad)
        ttk.Button(frm_top, text="Browse...", command=self._choose_dir).grid(row=0, column=4, sticky="we", **pad)

        frm_top.columnconfigure(1, weight=1)
        frm_top.columnconfigure(3, weight=1)

        frm_opts = ttk.LabelFrame(self, text="Options")
        frm_opts.pack(fill="x", padx=8, pady=4)

        ttk.Checkbutton(frm_opts, text=".txt", variable=self.var_txt).grid(row=0, column=0, sticky="w", padx=10, pady=4)
        ttk.Checkbutton(frm_opts, text=".log", variable=self.var_log).grid(row=0, column=1, sticky="w", padx=10, pady=4)
        ttk.Checkbutton(frm_opts, text=".csv", variable=self.var_csv).grid(row=0, column=2, sticky="w", padx=10, pady=4)
        ttk.Checkbutton(frm_opts, text=".xml", variable=self.var_xml).grid(row=0, column=3, sticky="w", padx=10, pady=4)
        ttk.Checkbutton(frm_opts, text=".json", variable=self.var_json).grid(row=0, column=4, sticky="w", padx=10, pady=4)

        ttk.Label(frm_opts, text="Custom wildcard:").grid(row=0, column=5, sticky="e")
        ttk.Entry(frm_opts, textvariable=self.var_custom, width=16).grid(row=0, column=6, sticky="w", padx=6)

        ttk.Checkbutton(frm_opts, text="Case sensitive", variable=self.var_case).grid(row=1, column=0, sticky="w", padx=10, pady=4)
        ttk.Checkbutton(frm_opts, text="Include subdirectories", variable=self.var_recursive).grid(row=1, column=1, sticky="w", padx=10, pady=4)

        frm_btns = ttk.Frame(self)
        frm_btns.pack(fill="x", padx=8, pady=4)
        ttk.Button(frm_btns, text="Start Search", command=self._start_search).pack(side="left")
        ttk.Button(frm_btns, text="Export Results", command=self._export).pack(side="left", padx=6)
        ttk.Button(frm_btns, text="Clear", command=self._clear).pack(side="left", padx=6)
        ttk.Button(frm_btns, text="Exit", command=self.destroy).pack(side="right")

        # results tree
        frm_tree = ttk.Frame(self)
        frm_tree.pack(fill="both", expand=True, padx=8, pady=4)

        columns = ("file", "line", "text")
        self.tree = ttk.Treeview(frm_tree, columns=columns, show="headings")
        self.tree.heading("file", text="File")
        self.tree.heading("line", text="Line")
        self.tree.heading("text", text="Content")

        self.tree.column("file", width=480, anchor="w")
        self.tree.column("line", width=60, anchor="center")
        self.tree.column("text", width=400, anchor="w")

        vsb = ttk.Scrollbar(frm_tree, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(frm_tree, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        frm_tree.rowconfigure(0, weight=1)
        frm_tree.columnconfigure(0, weight=1)

        self.tree.bind("<Double-1>", self._on_open_file)

        self.status = ttk.Label(self, text="Ready")
        self.status.pack(fill="x", padx=8, pady=6)

    def _choose_dir(self):
        d = filedialog.askdirectory(initialdir=self.var_dir.get() or os.getcwd())
        if d:
            self.var_dir.set(d)

    def _gather_patterns(self):
        pats = []
        if self.var_txt.get(): pats.append("*.txt")
        if self.var_log.get(): pats.append("*.log")
        if self.var_csv.get(): pats.append("*.csv")
        if self.var_xml.get(): pats.append("*.xml")
        if self.var_json.get(): pats.append("*.json")
        cust = self.var_custom.get().strip()
        if cust:
            pats.append(cust)
        if not pats:
            pats = ["*.txt"]
        return pats

    def _start_search(self):
        if self.worker and self.worker.is_alive():
            messagebox.showinfo("Please Wait", "Search in progress, please stop or wait for completion.")
            return
        term = self.var_search.get().strip()
        if not term:
            messagebox.showwarning("Missing Search Term", "Please enter a string to search.")
            return

        directory = self.var_dir.get().strip()
        recursive = self.var_recursive.get()
        case = self.var_case.get()
        patterns = self._gather_patterns()

        # reset counters & UI
        self._clear()
        self.status.config(text="Preparing search...")

        # spawn worker
        self.worker = threading.Thread(
            target=self._worker_search,
            args=(term, directory, recursive, case, patterns),
            daemon=True
        )
        self.worker.start()

    def _worker_search(self, term, directory, recursive, case, patterns):
        try:
            files = core.iter_files(directory, patterns, recursive=recursive)
            self.q.put(("meta", {"total_files": len(files)}))
            matched_files = 0
            total_hits = 0
            for fp in files:
                had = False
                try:
                    for line_no, line in core.iter_matches(fp, term, case):
                        self.q.put(("row", (fp, line_no, line)))
                        total_hits += 1
                        had = True
                except Exception as e:
                    self.q.put(("error", f"{fp}: {e}"))
                if had:
                    matched_files += 1
            self.q.put(("done", {"matched_files": matched_files, "total_hits": total_hits}))
        except Exception as e:
            self.q.put(("fatal", str(e)))

    def _drain_queue(self):
        try:
            while True:
                tag, payload = self.q.get_nowait()
                if tag == "meta":
                    self.total_files = payload["total_files"]
                    self.status.config(text=f"Found {self.total_files} candidate files, starting matching...")
                elif tag == "row":
                    fp, ln, text = payload
                    self.tree.insert("", "end", values=(fp, ln, text))
                elif tag == "error":
                    # Show but don't interrupt
                    print("[ERROR]", payload)
                elif tag == "done":
                    self.matched_files = payload["matched_files"]
                    self.total_hits = payload["total_hits"]
                    self.status.config(text=f"Complete: Found {self.total_hits} matches in {self.matched_files} files.")
                elif tag == "fatal":
                    messagebox.showerror("Search Failed", payload)
                    self.status.config(text="Failed")
        except queue.Empty:
            pass
        finally:
            self.after(120, self._drain_queue)

    def _export(self):
        if not self.tree.get_children():
            messagebox.showinfo("No Data", "No results to export.")
            return
        path = filedialog.asksaveasfilename(
            title="Export as CSV",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")]
        )
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["file", "line", "text"])
                for iid in self.tree.get_children():
                    row = self.tree.item(iid, "values")
                    w.writerow(row)
            messagebox.showinfo("Export Successful", f"Exported to: {path}")
        except Exception as e:
            messagebox.showerror("Export Failed", str(e))

    def _clear(self):
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        self.total_files = self.matched_files = self.total_hits = 0
        self.status.config(text="Ready")

    def _on_open_file(self, event):
        item = self.tree.identify_row(event.y)
        if not item:
            return
        fp, ln, _ = self.tree.item(item, "values")
        if not os.path.isfile(fp):
            messagebox.showwarning("File Does Not Exist", fp)
            return
        _open_in_os(fp)

def launch():
    app = SearchApp()
    app.mainloop()

if __name__ == "__main__":
    launch()