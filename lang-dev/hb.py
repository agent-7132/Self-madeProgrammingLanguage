import os

# 配置注释符号映射表
COMMENT_SYMBOLS = {
    '.py': '#',
    '.js': '//',
    '.c': '//',
    '.sol': '//',
    '.yaml': '#',
    '.json': '//',
    '.qs': '//',
    '.ll': ';',
    '.als': '--',
    '.v': '//',
    '.sh': '#',
    '.txt': '#',
    '.md': '<!--',
    '.sh': '#',
}

DEFAULT_SYMBOL = '#'
OUTPUT_FILE = 'merged_code.txt'
EXCLUDE_DIRS = {'__pycache__', '.git', '.idea'}  # 排除的目录

def get_comment_symbol(filename):
    """根据文件扩展名获取注释符号"""
    _, ext = os.path.splitext(filename)
    return COMMENT_SYMBOLS.get(ext.lower(), DEFAULT_SYMBOL)

def merge_files(root_dir, output_path):
    with open(output_path, 'w', encoding='utf-8') as outfile:
        for dirpath, dirnames, filenames in os.walk(root_dir):
            # 过滤排除目录
            dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
            
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(file_path, root_dir)
                symbol = get_comment_symbol(filename)

                try:
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        # 写入文件头
                        header = f"{symbol} File: {rel_path}\n{symbol}\n"
                        outfile.write(header)
                        
                        # 写入文件内容
                        content = infile.read()
                        outfile.write(content)
                        
                        # 添加分隔符
                        outfile.write('\n\n' + '-'*80 + '\n\n')
                        
                except UnicodeDecodeError:
                    # 处理二进制文件
                    warning = f"{symbol} [Binary file {rel_path} skipped]\n"
                    outfile.write(warning + '\n\n')
                except Exception as e:
                    error = f"{symbol} Error reading {rel_path}: {str(e)}\n"
                    outfile.write(error + '\n\n')

if __name__ == '__main__':
    project_root = '.'  # 设置为项目根目录路径
    merge_files(project_root, OUTPUT_FILE)
    print(f"All files merged into {OUTPUT_FILE}")
