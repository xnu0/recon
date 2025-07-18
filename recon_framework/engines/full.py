from typing import Dict, List, Any
from pathlib import Path
from core.logger import get_logger
from core.stealth import StealthManager
from core.database import ReconDatabase
from modules.subdomain import SubdomainModule
from modules.http import HTTPModule
from modules.vulnerability import VulnerabilityModule
from reports.generator import ReportGenerator

class FullReconEngine:
    def __init__(self, config, database: ReconDatabase):
        self.config = config
        self.database = database
        self.logger = get_logger('FullReconEngine')
        self.stealth_manager = StealthManager(config.__dict__)
        self.scan_id = None

    def run(self) -> Dict[str, Any]:
        self.scan_id = self.database.create_scan(self.config.target, 'full_recon', self.config.__dict__)
        try:
            subdomain_results = self.run_subdomain_enumeration()
            http_results = self.run_http_probing(subdomain_results['subdomains'])
            vuln_results = self.run_vulnerability_scanning([h['url'] for h in http_results['live_hosts']])
            report = self.generate_report()
            self.database.update_scan_status(self.scan_id, 'completed')
            return {
                'scan_id': self.scan_id,
                'target': self.config.target,
                'subdomain_results': subdomain_results,
                'http_results': http_results,
                'vulnerability_results': vuln_results,
                'report_path': report
            }
        except Exception as e:
            self.logger.error(f'Scan failed: {e}')
            self.database.update_scan_status(self.scan_id, 'failed')
            raise

    def run_subdomain_enumeration(self) -> Dict[str, Any]:
        module = SubdomainModule(self.config.__dict__, self.stealth_manager)
        results = module.run(self.config.target)
        for sub in results['subdomains']:
            self.database.add_subdomain(self.scan_id, sub)
        return results

    def run_http_probing(self, subdomains: List[str]) -> Dict[str, Any]:
        module = HTTPModule(self.config.__dict__, self.stealth_manager)
        results = module.run(subdomains)
        for host in results['live_hosts']:
            self.database.add_subdomain(self.scan_id, host.get('url', ''), status_code=host.get('status_code'), title=host.get('title'), technologies=host.get('technologies', []))
        return results

    def run_vulnerability_scanning(self, live_hosts: List[str]) -> Dict[str, Any]:
        module = VulnerabilityModule(self.config.__dict__, self.stealth_manager)
        results = module.run(live_hosts)
        for vuln in results['vulnerabilities']:
            self.database.add_vulnerability(self.scan_id, vuln.get('host', ''), vuln)
        return results

    def generate_report(self) -> str:
        generator = ReportGenerator(self.database)
        return generator.generate_report(self.config.target, self.config.output_dir, 'html')
