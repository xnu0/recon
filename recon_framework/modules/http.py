import os
import tempfile
from typing import List, Dict
from modules.base_module import BaseModule

class HTTPModule(BaseModule):
    def run(self, targets: List[str]) -> Dict[str, List[Dict]]:
        targets_file = self.write_targets_file(targets)
        try:
            hosts = self.run_httpx(targets_file)
            analyzed = self.analyze_responses(hosts)
            return {
                'live_hosts': hosts,
                'analyzed_results': analyzed,
                'total_live': len(hosts)
            }
        finally:
            if os.path.exists(targets_file):
                os.unlink(targets_file)

    def run_httpx(self, targets_file: str) -> List[Dict]:
        cmd = [
            'httpx', '-l', targets_file, '-json', '-silent',
            '-follow-redirects', '-status-code', '-title', '-tech-detect',
            '-content-length', '-timeout', str(self.config.get('timeout', 10))
        ]
        if self.config.get('mode') == 'stealth':
            cmd.extend(['-rate-limit', '10'])
        result = self.execute_tool(cmd)
        return self.parse_json_output(result.stdout)

    def write_targets_file(self, targets: List[str]) -> str:
        with tempfile.NamedTemporaryFile('w', suffix='.txt', delete=False) as f:
            for t in targets:
                f.write(f"{t}\n")
            return f.name

    def analyze_responses(self, responses: List[Dict]) -> List[Dict]:
        analyzed = []
        for r in responses:
            info = {
                'url': r.get('url'),
                'status_code': r.get('status_code'),
                'title': r.get('title'),
                'content_length': r.get('content_length'),
                'technologies': r.get('technologies', []),
                'interesting': []
            }
            if r.get('status_code') == 200:
                info['interesting'].append('HTTP 200 OK')
            if r.get('title') and any(k in r['title'].lower() for k in ['admin', 'login', 'dashboard']):
                info['interesting'].append('Admin/Login page detected')
            if r.get('technologies'):
                info['interesting'].append('Technologies: ' + ', '.join(r['technologies']))
            analyzed.append(info)
        return analyzed
