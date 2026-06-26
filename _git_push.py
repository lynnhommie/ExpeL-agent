"""一键推送到 GitHub"""
import subprocess, sys, os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

def run(cmd):
    print(f"\n$ {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if result.returncode != 0:
        print(f"⚠️ 返回码: {result.returncode}")
    return result

# 1. 检查状态
print("=" * 60)
print("📋 1. Git 状态")
print("=" * 60)
run("git status")

# 2. 检查远程仓库
print("\n" + "=" * 60)
print("📋 2. 远程仓库")
print("=" * 60)
run("git remote -v")

# 3. 检查分支
print("\n" + "=" * 60)
print("📋 3. 当前分支")
print("=" * 60)
run("git branch -a")

# 4. 看 .gitignore
print("\n" + "=" * 60)
print("📋 4. .gitignore")
print("=" * 60)
if os.path.exists(".gitignore"):
    with open(".gitignore") as f:
        print(f.read())
else:
    print("❌ 没有 .gitignore 文件!")
