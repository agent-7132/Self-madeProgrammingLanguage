import os
import logging

COMMENT_SYMBOLS = {
    '.py': '#',
    '.js': '//',
    '.c': '//',
    '.h': '//',
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
    '.jmx': '//',
}

DEFAULT_SYMBOL = '#'
EXCLUDE_DIRS = {'__pycache__', '.git', '.idea'}
MAX_SIZE = 30 * 1024
OUTPUT_TEMPLATE = 'code{0}.txt'

def get_comment_symbol(filename):
    _, ext = os.path.splitext(filename)
    return COMMENT_SYMBOLS.get(ext.lower(), DEFAULT_SYMBOL)

def is_binary(file_path):
    textchars = bytearray({7,8,9,10,12,13,27} | set(range(0x20, 0x100)) - {0x7f})
    with open(file_path, 'rb') as f:
        return bool(f.read(1024).translate(None, textchars))

def merge_files(root_dir):
    code_num = 1
    current_size = 0
    current_output = None

    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            
            try:
                if os.path.getsize(file_path) > MAX_SIZE or is_binary(file_path):
                    continue
                    
                comment = get_comment_symbol(filename)
                header = f"{comment} File: {filename}\n{comment}\n"
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                entry = f"{header}{content}\n\n"
                entry_size = len(entry.encode('utf-8'))
                
                if current_output is None or current_size + entry_size > MAX_SIZE:
                    if current_output is not None:
                        current_output.close()
                    output_path = OUTPUT_TEMPLATE.format(code_num)
                    current_output = open(output_path, 'w', encoding='utf-8')
                    code_num += 1
                    current_size = 0
                    
                current_output.write(entry)
                current_size += entry_size
                
            except Exception as e:
                logging.error(f"Error processing {file_path}: {str(e)}")
                continue
            
    if current_output is not None:
        current_output.close()

if __name__ == '__main__':
    merge_files('.')
