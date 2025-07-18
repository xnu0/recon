import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class ScanConfig:
    """Configuration for reconnaissance scans"""
    target: str
    mode: str = 'stealth'
    output_dir: str = './results'
    threads: int = 10
    timeout: int = 30
    delay_range: tuple = (1, 3)
    subfinder_config: Dict = field(default_factory=dict)
    nuclei_config: Dict = field(default_factory=dict)
    httpx_config: Dict = field(default_factory=dict)
    user_agents: List[str] = field(default_factory=list)
    proxies: List[str] = field(default_factory=list)
    output_formats: List[str] = field(default_factory=lambda: ['json', 'html'])

    @classmethod
    def from_file(cls, config_path: str) -> 'ScanConfig':
        with open(config_path, 'r') as f:
            data = yaml.safe_load(f)
        return cls(**data)

    @classmethod
    def from_profile(cls, profile_name: str, target: str) -> 'ScanConfig':
        profile_path = Path(__file__).parent.parent / 'config' / 'profiles.yaml'
        with open(profile_path, 'r') as f:
            profiles = yaml.safe_load(f)
        if profile_name not in profiles:
            raise ValueError(f"Profile '{profile_name}' not found")
        config = profiles[profile_name]
        config['target'] = target
        return cls(**config)
