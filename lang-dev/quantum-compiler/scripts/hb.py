import os
import logging
import hashlib
from functools import lru_cache

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
EXCLUDE_EXTS = {'.png', '.jpg', '.zip'}
MAX_SIZE = 1 * 1024 * 1024  # 1MB
OUTPUT_TEMPLATE = 'code{0}.txt'
CHECKPOINT_FILE = '.merge_progress'
CHUNK_SIZE = 8192

def get_comment_symbol(filename):
    _, ext = os.path.splitext(filename)
    ext = ext.lower()
    if ext in EXCLUDE_EXTS:
        return None
    return COMMENT_SYMBOLS.get(ext, DEFAULT_SYMBOL)

def file_hash(file_path):
    h = hashlib.md5()
    with open(file_path, 'rb') as f:
        while chunk := f.read(CHUNK_SIZE):
            h.update(chunk)
    return h.hexdigest()

def write_chunk(output_file, content_chunk):
    try:
        output_file.write(''.join(content_chunk))
        output_file.flush()
    except IOError as e:
        logging.error(f"写入失败: {str(e)}")
        raise

def merge_files(root_dir):
    processed_hashes = set()
    code_num = 1
    current_size = 0
    current_output = None
    
    # 加载进度
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, 'r') as f:
            processed_hashes = set(line.strip() for line in f)

    try:
        with open(CHECKPOINT_FILE, 'a') as progress:
            for dirpath, dirnames, filenames in os.walk(root_dir):
                dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
                
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    comment_symbol = get_comment_symbol(filename)
                    if not comment_symbol:
                        continue

                    try:
                        file_hash_value = file_hash(file_path)
                        if file_hash_value in processed_hashes:
                            continue
                        
                        header = f"{comment_symbol} File: {filename}\n{comment_symbol}\n"
                        content_chunk = [header]
                        
                        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                            for line in f:
                                content_chunk.append(line)
                                current_chunk_size = sum(len(c) for c in content_chunk)
                                
                                if current_chunk_size >= CHUNK_SIZE:
                                    if current_output is None or current_size + current_chunk_size > MAX_SIZE:
                                        if current_output:
                                            current_output.close()
                                        output_path = OUTPUT_TEMPLATE.format(code_num)
                                        current_output = open(output_path, 'w', encoding='utf-8')
                                        code_num += 1
                                        current_size = 0
                                    write_chunk(current_output, content_chunk)
                                    current_size += current_chunk_size
                                    content_chunk = []
                            
                            if content_chunk:
                                if current_output is None or current_size + sum(len(c) for c in content_chunk) > MAX_SIZE:
                                    if current_output:
                                        current_output.close()
                                    output_path = OUTPUT_TEMPLATE.format(code_num)
                                    current_output = open(output_path, 'w', encoding='utf-8')
                                    code_num += 1
                                    current_size = 0
                                write_chunk(current_output, content_chunk)
                                current_size += sum(len(c) for c in content_chunk)
                                
                        progress.write(f"{file_hash_value}\n")
                        progress.flush()
                        processed_hashes.add(file_hash_value)
                        
                    except (UnicodeDecodeError, OSError) as e:
                        logging.warning(f"跳过文件 {file_path}: {str(e)}")
                        continue

    finally:
        if current_output:
            current_output.close()
        if os.path.exists(CHECKPOINT_FILE):
            os.remove(CHECKPOINT_FILE)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    merge_files('.')
