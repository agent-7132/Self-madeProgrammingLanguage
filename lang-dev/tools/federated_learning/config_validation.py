import yaml
from typing import Dict, Any

class ConfigValidator:
    def __init__(self, config_path: str):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
    def validate(self) -> Dict[str, Any]:
        self._check_shard_ranges()
        self._validate_security_levels()
        return self.config
    
    def _check_shard_ranges(self):
        max_vocab = self.config['model']['params']['vocab_size']
        for node in self.config['federation']['nodes']:
            start, end = node['shard_range']
            if end > max_vocab * 1.2:
                raise ValueError(f"Shard range {end} exceeds 120% of vocab size")
            node['shard_range'] = [start, min(end, max_vocab)]
    
    def _validate_security_levels(self):
        levels = {n['security_level'] for n in self.config['federation']['nodes']}
        if max(levels) > 3:
            raise ValueError("Security level cannot exceed 3")
        
        # 文档2量子加密要求
        if self.config['quantum_security']['encryption'] not in ['Kyber-1024', 'NTRU']:
            raise ValueError("必须使用后量子加密算法")
            
        # 文档1包管理系统版本隔离要求
        if 'version_isolation' not in self.config['aggregation']:
            self.config['aggregation']['version_isolation'] = True
