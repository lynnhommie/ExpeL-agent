"""检查最终文件结构"""
import os
import sys

base = os.path.dirname(os.path.abspath(__file__))

skip_dirs = {"__pycache__", ".git", "logs"}
skip_ext = {".pyc", ".pkl", ".png"}

files = []
for root, dirs, fnames in os.walk(base):
    # 修改 dirs in-place 来跳过
    dirs[:] = [d for d in dirs if d not in skip_dirs and not d.startswith("__pycache__")]
    for f in fnames:
        ext = os.path.splitext(f)[1]
        if ext in skip_ext or f.endswith(".pyc"):
            continue
        rel = os.path.relpath(os.path.join(root, f), base)
        files.append(rel)

files.sort()
print(f"\n总文件数: {len(files)}\n")
for f in files:
    print(f"  {f}")
