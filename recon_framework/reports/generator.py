import json
from datetime import datetime
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from typing import Dict, Any

class ReportGenerator:
    def __init__(self, database):
        self.database = database
        self.template_dir = Path(__file__).parent / 'templates'
        self.env = Environment(loader=FileSystemLoader(str(self.template_dir)))

    def generate_report(self, target: str, output_dir: str, format: str = 'html') -> str:
        data = self.gather_report_data(target)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        if format == 'html':
            return self.generate_html_report(data, output_path)
        elif format == 'json':
            return self.generate_json_report(data, output_path)
        else:
            raise ValueError(f'Unsupported format: {format}')

    def gather_report_data(self, target: str) -> Dict[str, Any]:
        with self.database.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM scans WHERE target=? ORDER BY started_at DESC LIMIT 1", (target,))
            scan = cur.fetchone()
            if not scan:
                raise ValueError(f'No scan found for {target}')
            scan_id = scan['id']
            cur.execute("SELECT * FROM subdomains WHERE scan_id=? ORDER BY subdomain", (scan_id,))
            subs = cur.fetchall()
            cur.execute("SELECT * FROM vulnerabilities WHERE scan_id=? ORDER BY severity DESC", (scan_id,))
            vulns = cur.fetchall()
        return {
            'scan': dict(scan),
            'target': target,
            'subdomains': [dict(row) for row in subs],
            'vulnerabilities': [dict(row) for row in vulns],
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_subdomains': len(subs),
                'live_hosts': len([s for s in subs if s['status_code']]),
                'total_vulnerabilities': len(vulns)
            }
        }

    def generate_html_report(self, data: Dict[str, Any], output_path: Path) -> str:
        template = self.env.get_template('report.html')
        html = template.render(data=data)
        report_file = output_path / f"recon_report_{data['target']}.html"
        with open(report_file, 'w') as f:
            f.write(html)
        return str(report_file)

    def generate_json_report(self, data: Dict[str, Any], output_path: Path) -> str:
        report_file = output_path / f"recon_report_{data['target']}.json"
        with open(report_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        return str(report_file)
