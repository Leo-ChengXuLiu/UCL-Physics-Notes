import os
import shutil
import subprocess
from datetime import datetime

# ================= 配置区域 =================

# 1. 自动锁定当前脚本所在的文件夹作为“大本营”
REPO_ROOT = os.path.dirname(os.path.abspath(__file__))

# 2. 定义收件箱 (大本营里面的 _Inbox 文件夹)
INBOX_DIR = os.path.join(REPO_ROOT, "_Inbox")

# 3. 分类规则
CATEGORY_MAP = {
    "qm": "Quantum_Mechanics", "quantum": "Quantum_Mechanics", "schrodinger": "Quantum_Mechanics", "atom": "Quantum_Mechanics",
    "thermo": "Thermodynamics", "heat": "Thermodynamics", "thermal": "Thermodynamics",
    "mech": "Classical_Mechanics", "lagrangian": "Classical_Mechanics", "newton": "Classical_Mechanics",
    "em": "Electromagnetism", "electro": "Electromagnetism", "maxwell": "Electromagnetism", "optic": "Electromagnetism", "wave": "Electromagnetism",
    "lab": "Labs_and_Data",
    "python": "Computing", "code": "Computing",
    "math": "Math_Methods", "stats": "Math_Methods",
    "universe": "Astrophysics"
}
DEFAULT_FOLDER = "Uncategorized"

# ===========================================

def check_git_setup():
    """检查这里是不是一个 Git 仓库"""
    if not os.path.exists(os.path.join(REPO_ROOT, ".git")):
        print("⚠️ 警告：当前文件夹还不是 Git 仓库！")
        print("请在终端运行以下命令来初始化（只需运行一次）：")
        print(f"cd {REPO_ROOT}")
        print("git init")
        print("git remote add origin <你的GitHub地址>")
        return False
    return True

def git_push():
    """上传所有文件"""
    print("\n🚀 正在同步到 GitHub...")
    try:
        # 简单粗暴：添加当前目录下所有变动
        subprocess.run(["git", "add", "."], cwd=REPO_ROOT, check=True)
        
        # 检查有没有东西需要提交
        status = subprocess.run(["git", "status", "-s"], cwd=REPO_ROOT, capture_output=True, text=True)
        if not status.stdout.strip():
            print("😴 仓库没有变动，无需上传。")
            return

        commit_msg = f"Notes update: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=REPO_ROOT, check=True)
        
        # 推送
        subprocess.run(["git", "push", "origin", "main"], cwd=REPO_ROOT, check=True)
        print("✅ 成功！笔记已上传。")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git 操作出错: {e}")
        print("💡 提示：如果是第一次推送被拒绝，尝试在终端运行: git push -f origin main")

def organize_files():
    """整理文件"""
    if not os.path.exists(INBOX_DIR):
        os.makedirs(INBOX_DIR)
        print(f"已创建收件箱: {INBOX_DIR}")
        return

    files = [f for f in os.listdir(INBOX_DIR) if not f.startswith('.')]
    if not files:
        print("📭 收件箱 (_Inbox) 是空的，没有新笔记需要整理。")
        return

    print(f"🔍 发现 {len(files)} 个文件，开始分类...")
    for filename in files:
        src_path = os.path.join(INBOX_DIR, filename)
        if os.path.isdir(src_path): continue

        moved = False
        for keyword, folder_name in CATEGORY_MAP.items():
            if keyword in filename.lower():
                dest_dir = os.path.join(REPO_ROOT, folder_name)
                os.makedirs(dest_dir, exist_ok=True)
                shutil.move(src_path, os.path.join(dest_dir, filename))
                print(f"moved: {filename} -> 📂 {folder_name}")
                moved = True
                break
        
        if not moved:
            dest_dir = os.path.join(REPO_ROOT, DEFAULT_FOLDER)
            os.makedirs(dest_dir, exist_ok=True)
            shutil.move(src_path, os.path.join(dest_dir, filename))
            print(f"moved: {filename} -> 📂 {DEFAULT_FOLDER}")

if __name__ == "__main__":
    print(f"--- 运行位置: {REPO_ROOT} ---")
    if check_git_setup():
        organize_files()
        git_push()
    print("-------------------------")