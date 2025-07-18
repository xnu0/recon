from typing import List, Dict
from modules.base_module import BaseModule

class SubdomainModule(BaseModule):
    def __init__(self, config: Dict, stealth_manager=None):
        super().__init__(config, stealth_manager)
        self.tools = ['subfinder', 'amass', 'assetfinder']
        self.wordlists = config.get('wordlists', [])

    def run(self, target: str) -> Dict[str, List[str]]:
        if not self.validate_target(target):
            raise ValueError(f'Invalid target: {target}')
        all_subdomains = set()
        tool_results = {}
        for tool in self.tools:
            try:
                subs = self.run_tool(tool, target)
                tool_results[tool] = subs
                all_subdomains.update(subs)
            except Exception as e:
                self.logger.error(f'{tool} failed: {e}')
                self.errors.append(f'{tool}: {e}')
        final_subdomains = sorted(all_subdomains)
        return {
            'subdomains': final_subdomains,
            'tool_results': tool_results,
            'total_count': len(final_subdomains)
        }

    def run_tool(self, tool: str, target: str) -> List[str]:
        if tool == 'subfinder':
            return self.run_subfinder(target)
        if tool == 'amass':
            return self.run_amass(target)
        if tool == 'assetfinder':
            return self.run_assetfinder(target)
        return []

    def run_subfinder(self, target: str) -> List[str]:
        cmd = ['subfinder', '-d', target, '-silent']
        if self.config.get('api_keys'):
            config_file = self.create_subfinder_config()
            cmd.extend(['-config', config_file])
        result = self.execute_tool(cmd)
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]

    def run_amass(self, target: str) -> List[str]:
        cmd = ['amass', 'enum', '-d', target, '-silent']
        if self.config.get('mode') == 'stealth':
            cmd.append('-passive')
        result = self.execute_tool(cmd)
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]

    def run_assetfinder(self, target: str) -> List[str]:
        cmd = ['assetfinder', target]
        try:
            result = self.execute_tool(cmd)
            return [line.strip() for line in result.stdout.splitlines() if line.strip()]
        except Exception as e:
            self.logger.warning(f'assetfinder failed: {e}')
            return []

    def create_subfinder_config(self) -> str:
        import tempfile
        import yaml
        config = {
            'virustotal': [self.config['api_keys'].get('virustotal', '')],
            'shodan': [self.config['api_keys'].get('shodan', '')],
            'censys': [self.config['api_keys'].get('censys', '')],
            'chaos': [self.config['api_keys'].get('chaos', '')]
        }
        with tempfile.NamedTemporaryFile('w', suffix='.yaml', delete=False) as f:
            yaml.dump(config, f)
            return f.name
