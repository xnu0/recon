import random
import time
from typing import List, Dict, Optional
import requests

class StealthManager:
    def __init__(self, config: Dict):
        self.config = config
        self.mode = config.get('mode', 'normal')
        self.delay_range = config.get('delay_range', (0.1, 0.5))
        self.user_agents = config.get('user_agents', self._default_user_agents())
        self.proxies = config.get('proxies', [])
        self.session = requests.Session()

    def _default_user_agents(self) -> List[str]:
        return [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
        ]

    def apply_delay(self):
        if self.mode == 'stealth':
            delay = random.uniform(2, 5)
        elif self.mode == 'normal':
            delay = random.uniform(0.5, 1.5)
        else:
            delay = random.uniform(0.01, 0.1)
        time.sleep(delay)

    def get_headers(self) -> Dict[str, str]:
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }

    def get_proxy(self) -> Optional[Dict[str, str]]:
        if self.proxies:
            proxy = random.choice(self.proxies)
            return {'http': proxy, 'https': proxy}
        return None
