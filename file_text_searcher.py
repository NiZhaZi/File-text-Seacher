import os
import glob

def search_in_files(search_string, file_extension="*.txt", case_sensitive=False):
    """
    Search for string in all specified files in current directory
    
    Parameters:
    search_string: string to search for
    file_extension: file extension, default is "*.txt"
    case_sensitive: whether to be case sensitive, default is False
    """
    # Get all specified files in current directory
    files = glob.glob(file_extension)
    
    if not files:
        print(f"No {file_extension} files found in current directory")
        return
    
    print(f"Searching for '{search_string}' in {len(files)} files...\n")
    
    found_count = 0
    
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                lines = content.split('\n')
                
                # Search based on case sensitivity setting
                if case_sensitive:
                    search_content = content
                    search_target = search_string
                else:
                    search_content = content.lower()
                    search_target = search_string.lower()
                
                # Check if contains search string
                if search_target in search_content:
                    found_count += 1
                    print(f"🔍 Found match in file '{file_path}':")
                    
                    # Display lines containing search string
                    for line_num, line in enumerate(lines, 1):
                        if case_sensitive:
                            if search_string in line:
                                print(f"   Line {line_num}: {line.strip()}")
                        else:
                            if search_string.lower() in line.lower():
                                print(f"   Line {line_num}: {line.strip()}")
                    print("-" * 50)
                    
        except UnicodeDecodeError:
            # If UTF-8 decoding fails, try other encodings
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
                        print(f"🔍 Found match in file '{file_path}':")
                        
                        for line_num, line in enumerate(lines, 1):
                            if case_sensitive:
                                if search_string in line:
                                    print(f"   Line {line_num}: {line.strip()}")
                            else:
                                if search_string.lower() in line.lower():
                                    print(f"   Line {line_num}: {line.strip()}")
                        print("-" * 50)
                        
            except Exception as e:
                print(f"❌ Unable to read file '{file_path}': {e}")
                
        except Exception as e:
            print(f"❌ Error processing file '{file_path}': {e}")
    
    print(f"\nSearch completed! Found '{search_string}' in {found_count} files")

def search_with_options():
    """
    Provide interactive search options
    """
    print("=== Text File Search Tool ===")
    
    # Get search string
    search_string = input("Enter the string to search for: ").strip()
    if not search_string:
        print("Search string cannot be empty!")
        return
    
    # Select file type
    print("\nPlease select file type:")
    print("1. .txt files")
    print("2. .log files") 
    print("3. .csv files")
    print("4. .xml files")
    print("5. .json files")
    print("6. All text files (*.txt, *.log, *.csv, *.xml, *.json)")
    print("7. Custom file extension")
    
    choice = input("Please choose (1-7): ").strip()
    
    file_extensions = {
        '1': "*.txt",
        '2': "*.log", 
        '3': "*.csv",
        '4': "*.xml",
        '5': "*.json",
        '6': ["*.txt", "*.log", "*.csv", "*.xml", "*.json"]
    }
    
    if choice == '7':
        custom_ext = input("Enter file extension (e.g., *.py, *.md): ").strip()
        file_extension = custom_ext
    elif choice in file_extensions:
        file_extension = file_extensions[choice]
    else:
        print("Invalid choice, using .txt files by default")
        file_extension = "*.txt"
    
    # Case sensitivity
    case_sensitive = input("Case sensitive? (y/N): ").strip().lower() == 'y'
    
    print("\nStarting search...")
    
    # If multiple extensions, search each one
    if isinstance(file_extension, list):
        for ext in file_extension:
            search_in_files(search_string, ext, case_sensitive)
    else:
        search_in_files(search_string, file_extension, case_sensitive)

def batch_search():
    """
    Batch search for multiple strings
    """
    print("=== Batch Search Mode ===")
    
    # Get multiple search strings
    print("Enter multiple strings to search for (separated by commas):")
    search_strings_input = input().strip()
    
    if not search_strings_input:
        print("Search strings cannot be empty!")
        return
        
    search_strings = [s.strip() for s in search_strings_input.split(',') if s.strip()]
    
    file_extension = input("Enter file extension (default: *.txt): ").strip()
    if not file_extension:
        file_extension = "*.txt"
    
    case_sensitive = input("Case sensitive? (y/N): ").strip().lower() == 'y'
    
    for search_string in search_strings:
        print(f"\nSearching for: '{search_string}'")
        search_in_files(search_string, file_extension, case_sensitive)

if __name__ == "__main__":
    while True:
        print("\n" + "="*50)
        print("Text File Search Tool")
        print("="*50)
        print("1. Single search")
        print("2. Batch search multiple strings") 
        print("3. Exit")
        
        choice = input("Select mode (1-3): ").strip()
        
        if choice == '1':
            search_with_options()
        elif choice == '2':
            batch_search()
        elif choice == '3':
            print("Goodbye!")
            break
        else:
            print("Invalid choice, please try again!")