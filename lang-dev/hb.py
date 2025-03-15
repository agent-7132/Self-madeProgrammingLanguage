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
            rel_path = os.path.relpath(file_path, root_dir)
            comment_symbol = get_comment_symbol(filename)
            
            # 构建带注释的文件内容
            try:
                with open(file_path, 'r', encoding='utf-8') as infile:
                    content_block = (
                        f"{comment_symbol} ==== {rel_path} ====\n"
                        f"{infile.read()}\n\n"
                    )
            except UnicodeDecodeError:
                continue  # 跳过二进制文件
            except Exception:
                continue  # 跳过无权限文件
            
            # 计算内容字节长度
            content_bytes = content_block.encode('utf-8')
            content_len = len(content_bytes)
            
            # 分卷控制逻辑
            if current_output:
                if current_size + content_len > MAX_SIZE:
                    current_output.close()
                    code_num += 1
                    current_output = None
            
            if not current_output:
                output_path = OUTPUT_TEMPLATE.format(code_num)
                current_output = open(output_path, 'w', encoding='utf-8')
                current_size = 0
            
            # 写入内容并更新大小
            current_output.write(content_block)
            current_size += content_len
    
    # 关闭最后一个分卷文件
    if current_output:
        current_output.close()

# 使用示例
if __name__ == '__main__':
    merge_files('.')  # 合并当前目录
