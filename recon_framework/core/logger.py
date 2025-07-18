from loguru import logger
from pathlib import Path

_loggers = {}

def get_logger(name: str):
    if name in _loggers:
        return _loggers[name]

    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"{name}.log"
    _logger = logger.bind(name=name)
    _logger.add(log_file, rotation='1 MB', retention=5)
    _loggers[name] = _logger
    return _logger
