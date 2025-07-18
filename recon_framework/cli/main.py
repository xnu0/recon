import json
from pathlib import Path
import click
from core.config import ScanConfig
from core.logger import get_logger
from core.database import ReconDatabase
from engines.full import FullReconEngine

@click.group()
@click.version_option(version='1.0.0')
def cli():
    """Recon framework"""
    pass

@cli.command()
@click.argument('target')
@click.option('--mode', '-m', default='normal', type=click.Choice(['stealth', 'normal', 'aggressive']))
@click.option('--profile', '-p')
@click.option('--config', '-c')
@click.option('--output', '-o', default='./results')
@click.option('--threads', '-t', default=10)
@click.option('--timeout', default=30)
def scan(target, mode, profile, config, output, threads, timeout):
    if config:
        cfg = ScanConfig.from_file(config)
    elif profile:
        cfg = ScanConfig.from_profile(profile, target)
    else:
        cfg = ScanConfig(target=target, mode=mode, output_dir=output, threads=threads, timeout=timeout)

    cfg.target = target
    cfg.mode = mode
    cfg.output_dir = output
    cfg.threads = threads
    cfg.timeout = timeout

    Path(output).mkdir(parents=True, exist_ok=True)

    logger = get_logger('ReconFramework')
    db = ReconDatabase(f"{output}/recon.db")
    engine = FullReconEngine(cfg, db)

    try:
        logger.info(f"Starting scan on {target}")
        results = engine.run()
        with open(f"{output}/results.json", 'w') as f:
            json.dump(results, f, indent=2)
        click.echo(f"Results saved to {output}/results.json")
    except Exception as e:
        logger.error(f"Scan failed: {e}")
        click.echo(f"Error: {e}", err=True)

@cli.command()
@click.argument('target')
@click.option('--output', '-o', default='./reports')
@click.option('--format', '-f', default='html', type=click.Choice(['html', 'json']))
def report(target, output, format):
    db_path = Path('./results/recon.db')
    if not db_path.exists():
        click.echo('No scan results found', err=True)
        return
    db = ReconDatabase(str(db_path))
    from reports.generator import ReportGenerator
    gen = ReportGenerator(db)
    report_file = gen.generate_report(target, output, format)
    click.echo(f"Report generated: {report_file}")

if __name__ == '__main__':
    cli()
