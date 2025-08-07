"""
XuanXue包安装脚本
"""
from setuptools import setup, find_packages
import os

# 读取README文件
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "XuanXue - 玄学数据分析包"

# 读取requirements
def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(req_path):
        with open(req_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return ['sxtwl']

setup(
    name="xuanxue",
    version="1.0.0",
    author="XuWu",
    author_email="your.email@example.com",
    description="玄学数据分析包 - 干支计算和股票分析工具",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/xuanxue",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial",
        "Topic :: Scientific/Engineering",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    include_package_data=True,
    package_data={
        'XuanXue': ['*.txt', '*.md'],
        'XuanXue.xuanxue.config': ['*.txt'],
    },
    entry_points={
        'console_scripts': [
            'xuanxue=XuanXue.xuanxue.cli:main',
        ],
    },
    keywords="ganzhi, stock, finance, chinese-calendar, xuanxue",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/xuanxue/issues",
        "Source": "https://github.com/yourusername/xuanxue",
        "Documentation": "https://github.com/yourusername/xuanxue/wiki",
    },
)