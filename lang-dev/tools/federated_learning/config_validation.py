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
                raise ValueError(f"分片范围 {end} 超过词表大小的120%")
            node['shard_range'] = [start, min(end, max_vocab)]
    
    def _validate_security_levels(self):
        levels = {n['security_level'] for n in self.config['federation']['nodes']}
        if max(levels) > 3:
            raise ValueError("安全级别不能超过3")
        
        if 'quantum_security' in self.config:
            required_fields = ['key_exchange', 'encryption']
            for field in required_fields:
                if field not in self.config['quantum_security']:
                    raise ValueError(f"缺失必要的安全字段: {field}")

if __name__ == "__main__":
    validator = ConfigValidator("config_v2.yaml")
    validated_config = validator.validate()
    print("配置文件验证通过:", validated_config)
