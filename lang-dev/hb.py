import os

# 配置注释符号映射表
COMMENT_SYMBOLS = {
    '.py': '#',
    '.js': '//',
    '.c': '//',
    '.h': '//',  # 新增对.h文件的支持
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
    '.jmx': '//',  # 根据需求添加
}

DEFAULT_SYMBOL = '#'
EXCLUDE_DIRS = {'__pycache__', '.git', '.idea'}  # 排除的目录
MAX_SIZE = 30 * 1024  # 30KB阈值
OUTPUT_TEMPLATE = 'code{0}.txt'  # 分卷文件名模板

def get_comment_symbol(filename):
    """根据文件扩展名获取注释符号"""
    _, ext = os.path.splitext(filename)
    return COMMENT_SYMBOLS.get(ext.lower(), DEFAULT_SYMBOL)

def merge_files(root_dir):
    """合并目录文件并按30KB分卷"""
    code_num = 1
    current_size = 0
    current_output = None

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # 过滤排除目录
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            
            # 跳过超过阈值的大文件
            if os.path.getsize(file_path) > MAX_SIZE:
                continue
                
            comment = get_comment_symbol(filename)
            header = f"{comment} File: {filename}\n{comment}\n"
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                continue  # 跳过二进制文件
                
            entry = f"{header}{content}\n\n"
            entry_size = len(entry.encode('utf-8'))
            
            # 需要创建新分卷的情况
            if current_output is None or current_size + entry_size > MAX_SIZE:
                if current_output is not None:
                    current_output.close()
                output_path = OUTPUT_TEMPLATE.format(code_num)
                current_output = open(output_path, 'w', encoding='utf-8')
                code_num += 1
                current_size = 0
                
            # 写入内容
            current_output.write(entry)
            current_size += entry_size
            
    if current_output is not None:
        current_output.close()

if __name__ == '__main__':
    merge_files('.')
