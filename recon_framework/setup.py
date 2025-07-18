from setuptools import setup, find_packages

setup(
    name='recon_framework',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'click>=8.0.0',
        'pyyaml>=6.0',
        'jinja2>=3.0.0',
        'requests>=2.25.0',
        'loguru>=0.6.0',
        'weasyprint>=56.0'
    ],
    entry_points={'console_scripts': ['recon=recon_framework.cli.main:cli']}
)
