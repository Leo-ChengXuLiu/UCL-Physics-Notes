import os
import shutil
import subprocess
import requests
import json
from datetime import datetime

# ================= 配置区域 =================
REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
INBOX_DIR = os.path.join(REPO_ROOT, "_Inbox")
DEFAULT_FOLDER = "Uncategorized"

# AI 配置 (本地 Ollama)
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"  # 确保你终端里 pull 的是这个名字
# ===========================================

def ask_ai_for_folder(filename):
    """
    把文件名发给本地 AI，让它通过物理知识判断属于哪个分类
    """
    print(f"🤖 正在询问 AI 如何分类: '{filename}' ...")
    
    # 这是一个精心设计的 Prompt (提示词)，教 AI 怎么做
    prompt = f"""
    You are a helpful assistant for a Physics student at UCL.
    Task: Categorize the following course file into a single, concise folder name (in English).
    
    Filename: "{filename}"
    
    Rules:
    1. Use standard physics categories like: Quantum_Mechanics, Thermodynamics, Electromagnetism, Classical_Mechanics, Math_Methods, Astrophysics, Computing, Labs.
    2. If it's clearly a specific topic (e.g., "triso fuel"), generalize it (e.g., "Nuclear_Physics").
    3. Output ONLY the folder name. Do not output anything else. No punctuation.
    4. If you represent uncertain, output "Uncategorized".
    
    Folder Name:
    """

    try:
        response = requests.post(OLLAMA_URL, json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        })
        
        if response.status_code == 200:
            result = response.json().get("response", "").strip()
            # 清理一下 AI 可能产生的多余符号
            folder_name = result.replace(" ", "_").replace(".", "").replace('"', "")
            print(f"💡 AI 决定放入: 📂 {folder_name}")
            return folder_name
        else:
            print(f"⚠️ AI 响应错误: {response.status_code}")
            return DEFAULT_FOLDER
            
    except Exception as e:
        print(f"⚠️ 连接本地 AI 失败 (你打开 Ollama App 了吗?): {e}")
        return DEFAULT_FOLDER

def git_push():
    """Git 同步功能"""
    print("\n🚀 正在同步到 GitHub...")
    try:
        subprocess.run(["git", "add", "."], cwd=REPO_ROOT, check=True)
        
        status = subprocess.run(["git", "status", "-s"], cwd=REPO_ROOT, capture_output=True, text=True)
        if not status.stdout.strip():
            print("😴 仓库没有变动，无需上传。")
            return

        commit_msg = f"AI Update: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=REPO_ROOT, check=True)
        subprocess.run(["git", "push", "origin", "main"], cwd=REPO_ROOT, check=True)
        print("✅ 成功！笔记已上传。")
    except subprocess.CalledProcessError as e:
        print(f"❌ Git 操作出错: {e}")

def organize_files():
    """遍历文件并调用 AI"""
    if not os.path.exists(INBOX_DIR):
        os.makedirs(INBOX_DIR)
        return

    files = [f for f in os.listdir(INBOX_DIR) if not f.startswith('.')]
    if not files:
        print("📭 Inbox 空空如也。")
        return

    for filename in files:
        src_path = os.path.join(INBOX_DIR, filename)
        if os.path.isdir(src_path): continue

        # === 关键改动：不再查字典，而是问 AI ===
        folder_name = ask_ai_for_folder(filename)
        # ====================================
        
        dest_dir = os.path.join(REPO_ROOT, folder_name)
        os.makedirs(dest_dir, exist_ok=True)
        
        shutil.move(src_path, os.path.join(dest_dir, filename))

if __name__ == "__main__":
    print(f"--- 🧠 AI 智能整理模式 ---")
    organize_files()
    git_push()
    print("-------------------------")