import os
import glob

def search_in_files(search_string, file_extension="*.txt", case_sensitive=False):
    """
    在当前目录的所有指定类型文件中搜索字符串
    
    参数:
    search_string: 要搜索的字符串
    file_extension: 文件扩展名，默认为"*.txt"
    case_sensitive: 是否区分大小写，默认为False
    """
    # 获取当前目录下所有指定类型的文件
    files = glob.glob(file_extension)
    
    if not files:
        print(f"在当前目录下没有找到 {file_extension} 文件")
        return
    
    print(f"正在搜索 '{search_string}' 在 {len(files)} 个文件中...\n")
    
    found_count = 0
    
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                lines = content.split('\n')
                
                # 根据是否区分大小写进行搜索
                if case_sensitive:
                    search_content = content
                    search_target = search_string
                else:
                    search_content = content.lower()
                    search_target = search_string.lower()
                
                # 检查是否包含搜索字符串
                if search_target in search_content:
                    found_count += 1
                    print(f"🔍 在文件 '{file_path}' 中找到匹配:")
                    
                    # 显示包含搜索字符串的行
                    for line_num, line in enumerate(lines, 1):
                        if case_sensitive:
                            if search_string in line:
                                print(f"   第 {line_num} 行: {line.strip()}")
                        else:
                            if search_string.lower() in line.lower():
                                print(f"   第 {line_num} 行: {line.strip()}")
                    print("-" * 50)
                    
        except UnicodeDecodeError:
            # 如果UTF-8解码失败，尝试其他编码
            try:
                with open(file_path, 'r', encoding='gbk') as file:
                    content = file.read()
                    lines = content.split('\n')
                    
                    if case_sensitive:
                        search_content = content
                        search_target = search_string
                    else:
                        search_content = content.lower()
                        search_target = search_string.lower()
                    
                    if search_target in search_content:
                        found_count += 1
                        print(f"🔍 在文件 '{file_path}' 中找到匹配:")
                        
                        for line_num, line in enumerate(lines, 1):
                            if case_sensitive:
                                if search_string in line:
                                    print(f"   第 {line_num} 行: {line.strip()}")
                            else:
                                if search_string.lower() in line.lower():
                                    print(f"   第 {line_num} 行: {line.strip()}")
                        print("-" * 50)
                        
            except Exception as e:
                print(f"❌ 无法读取文件 '{file_path}': {e}")
                
        except Exception as e:
            print(f"❌ 处理文件 '{file_path}' 时出错: {e}")
    
    print(f"\n搜索完成！在 {found_count} 个文件中找到了 '{search_string}'")

def search_with_options():
    """
    提供交互式搜索选项
    """
    print("=== 文本文件搜索工具 ===")
    
    # 获取搜索字符串
    search_string = input("请输入要搜索的字符串: ").strip()
    if not search_string:
        print("搜索字符串不能为空！")
        return
    
    # 选择文件类型
    print("\n请选择文件类型:")
    print("1. .txt 文件")
    print("2. .log 文件") 
    print("3. .csv 文件")
    print("4. .xml 文件")
    print("5. .json 文件")
    print("6. 所有文本文件 (*.txt, *.log, *.csv, *.xml, *.json)")
    print("7. 自定义文件扩展名")
    
    choice = input("请选择 (1-7): ").strip()
    
    file_extensions = {
        '1': "*.txt",
        '2': "*.log", 
        '3': "*.csv",
        '4': "*.xml",
        '5': "*.json",
        '6': ["*.txt", "*.log", "*.csv", "*.xml", "*.json"]
    }
    
    if choice == '7':
        custom_ext = input("请输入文件扩展名 (例如: *.py, *.md): ").strip()
        file_extension = custom_ext
    elif choice in file_extensions:
        file_extension = file_extensions[choice]
    else:
        print("无效选择，默认使用 .txt 文件")
        file_extension = "*.txt"
    
    # 是否区分大小写
    case_sensitive = input("是否区分大小写? (y/N): ").strip().lower() == 'y'
    
    print("\n开始搜索...")
    
    # 如果是多个扩展名，分别搜索
    if isinstance(file_extension, list):
        for ext in file_extension:
            search_in_files(search_string, ext, case_sensitive)
    else:
        search_in_files(search_string, file_extension, case_sensitive)

def batch_search():
    """
    批量搜索多个字符串
    """
    print("=== 批量搜索模式 ===")
    
    # 获取多个搜索字符串
    print("请输入要搜索的多个字符串（用逗号分隔）:")
    search_strings_input = input().strip()
    
    if not search_strings_input:
        print("搜索字符串不能为空！")
        return
        
    search_strings = [s.strip() for s in search_strings_input.split(',') if s.strip()]
    
    file_extension = input("请输入文件扩展名 (默认: *.txt): ").strip()
    if not file_extension:
        file_extension = "*.txt"
    
    case_sensitive = input("是否区分大小写? (y/N): ").strip().lower() == 'y'
    
    for search_string in search_strings:
        print(f"\n搜索字符串: '{search_string}'")
        search_in_files(search_string, file_extension, case_sensitive)

if __name__ == "__main__":
    while True:
        print("\n" + "="*50)
        print("文本文件搜索工具")
        print("="*50)
        print("1. 单次搜索")
        print("2. 批量搜索多个字符串") 
        print("3. 退出")
        
        choice = input("请选择模式 (1-3): ").strip()
        
        if choice == '1':
            search_with_options()
        elif choice == '2':
            batch_search()
        elif choice == '3':
            print("再见！")
            break
        else:
            print("无效选择，请重新输入！")