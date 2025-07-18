import subprocess
import json
import tempfile
import re
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from core.logger import get_logger
from core.exceptions import ModuleException

class BaseModule(ABC):
    def __init__(self, config: Dict, stealth_manager=None):
        self.config = config
        self.stealth_manager = stealth_manager
        self.logger = get_logger(self.__class__.__name__)
        self.results = []
        self.errors = []

    @abstractmethod
    def run(self, target: str):
        pass

    def execute_tool(self, command: List[str], timeout: int = 300) -> subprocess.CompletedProcess:
        try:
            if self.stealth_manager:
                self.stealth_manager.apply_delay()
            self.logger.info('Executing command: %s', ' '.join(command))
            result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
            if result.returncode != 0 and result.stderr:
                self.logger.warning(f"stderr: {result.stderr}")
            return result
        except subprocess.TimeoutExpired:
            self.logger.error('Timeout expired for command: %s', ' '.join(command))
            raise ModuleException('Timeout executing tool')
        except FileNotFoundError:
            self.logger.error('Tool not found: %s', command[0])
            raise ModuleException('Tool not found')
        except Exception as e:
            self.logger.error('Execution failed: %s', e)
            raise ModuleException(str(e))

    def parse_json_output(self, output: str) -> List[Dict]:
        items = []
        for line in output.strip().split('\n'):
            if line.strip():
                try:
                    items.append(json.loads(line))
                except json.JSONDecodeError:
                    self.logger.warning('Failed to parse line: %s', line)
        return items

    def write_temp_file(self, content: str, suffix: str = '.tmp') -> str:
        with tempfile.NamedTemporaryFile('w', suffix=suffix, delete=False) as f:
            f.write(content)
            return f.name

    def validate_target(self, target: str) -> bool:
        pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$'
        return bool(re.match(pattern, target))
