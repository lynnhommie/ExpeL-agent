"""快速生成图表脚本"""
import subprocess, sys, os

# 先确保安装
subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib", "numpy", "-q"])

os.chdir(os.path.dirname(os.path.abspath(__file__)))

exec(open("generate_report_charts.py", encoding="utf-8").read())
