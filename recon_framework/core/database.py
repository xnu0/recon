import sqlite3
import json
from datetime import datetime
from contextlib import contextmanager
from typing import Dict

class ReconDatabase:
    """SQLite database handler"""
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        with self.get_connection() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS scans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target TEXT NOT NULL,
                    scan_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    started_at TIMESTAMP NOT NULL,
                    completed_at TIMESTAMP,
                    config TEXT
                );
                CREATE TABLE IF NOT EXISTS subdomains (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_id INTEGER,
                    subdomain TEXT NOT NULL,
                    ip_address TEXT,
                    status_code INTEGER,
                    title TEXT,
                    technologies TEXT,
                    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (scan_id) REFERENCES scans (id)
                );
                CREATE TABLE IF NOT EXISTS vulnerabilities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_id INTEGER,
                    target TEXT NOT NULL,
                    template_id TEXT,
                    severity TEXT,
                    description TEXT,
                    matched_at TEXT,
                    raw_output TEXT,
                    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (scan_id) REFERENCES scans (id)
                );
                CREATE TABLE IF NOT EXISTS secrets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_id INTEGER,
                    target TEXT NOT NULL,
                    secret_type TEXT,
                    secret_value TEXT,
                    file_path TEXT,
                    line_number INTEGER,
                    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (scan_id) REFERENCES scans (id)
                );
                """
            )

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def create_scan(self, target: str, scan_type: str, config: Dict) -> int:
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """INSERT INTO scans (target, scan_type, status, started_at, config)
                VALUES (?, ?, ?, ?, ?)""",
                (target, scan_type, 'running', datetime.now(), json.dumps(config))
            )
            conn.commit()
            return cur.lastrowid

    def update_scan_status(self, scan_id: int, status: str):
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """UPDATE scans SET status = ?, completed_at = ? WHERE id = ?""",
                (status, datetime.now(), scan_id)
            )
            conn.commit()

    def add_subdomain(self, scan_id: int, subdomain: str, **kwargs):
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """INSERT INTO subdomains (scan_id, subdomain, ip_address, status_code, title, technologies)
                VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    scan_id,
                    subdomain,
                    kwargs.get('ip_address'),
                    kwargs.get('status_code'),
                    kwargs.get('title'),
                    json.dumps(kwargs.get('technologies', []))
                )
            )
            conn.commit()

    def add_vulnerability(self, scan_id: int, target: str, vuln_data: Dict):
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """INSERT INTO vulnerabilities (scan_id, target, template_id, severity, description, matched_at, raw_output)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    scan_id,
                    target,
                    vuln_data.get('template_id'),
                    vuln_data.get('severity'),
                    vuln_data.get('description'),
                    vuln_data.get('matched_at'),
                    json.dumps(vuln_data)
                )
            )
            conn.commit()

