# 文本搜索工具（CLI + GUI）

> 本项目主要由AI生成

## 功能概览

- ✅ **可指定搜索目录**（输入为空时默认当前目录）
- ✅ **可选是否包含子目录**（递归）
- ✅ **支持常见文本类型**（`*.txt, *.log, *.csv, *.xml, *.json`）或自定义通配符
- ✅ **区分/不区分大小写** 选择
- ✅ **批量搜索多个关键词**
- ✅ **图形界面（Tkinter）**：目录选择、类型勾选、结果表格、导出 CSV、双击打开文件
- ✅ **命令行与交互式菜单** 保留

## 目录结构

```
text_searcher/
├─ CMakeLists.txt
├─ requirements.txt
├─ README.md
└─ src/
   ├─ file_text_searcher.py   # 核心搜索逻辑 + 交互式菜单
   ├─ main.py                 # 命令行入口（可启动 GUI）
   └─ gui_app.py              # Tkinter 图形界面
```

## 直接运行（无需打包）

确保已安装 Python 3.8+：

```bash
cd text_searcher/src
python main.py            # 进入交互式菜单（原体验保留）
python main.py --gui      # 启动图形界面
python main.py -s 关键字 -d 路径 -e *.txt -R  # 直接命令行搜索
```

常用参数：

- `-s/--search` 指定搜索词
- `-b/--batch`  批量搜索（多个词用空格分隔）
- `-d/--dir`    指定目录（留空=当前目录）
- `-e/--ext`    文件通配符（可重复，例如 `-e *.txt -e *.log`）
- `--all-types` 常见类型（`*.txt,*.log,*.csv,*.xml,*.json`）
- `-R/--recursive` 包含子目录
- `-i/--case-sensitive` 区分大小写
- `--gui` 启动图形界面
- `--interactive` 强制进入交互式菜单

## 使用 CMake 打包为可执行文件

1) 安装依赖：需要 **CMake 3.15+**、**Python 3.8+**、可执行的 **pip**。  
   - Linux 下 Tkinter 可能需要系统包（如 `sudo apt install python3-tk`）。
2) 生成并构建：

```bash
cd text_searcher
cmake -S . -B build
cmake --build build -j
```

构建完成后，可执行文件位于：

- `build/dist/TextSearcherCLI`（命令行）
- `build/dist/TextSearcherGUI`（图形界面）

> 注：本工程使用 **PyInstaller** 进行“冻结”打包，路径及依赖由 CMake 自动处理。

## GUI 使用要点

- “目录”可通过“选择...”按钮浏览选择；留空则默认当前工作目录。
- “自定义通配符”支持任意 glob（如 `*.py`、`*.*`）。
- 结果区域双击一行可在系统默认程序中打开文件。
- 支持将结果导出为 CSV。
