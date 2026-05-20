import os
import sys
import shutil
import subprocess

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'parser'))

from parse import analyze_repo
from db import save_repo

def clone_repo(repo_url, target_dir):
    if os.path.exists(target_dir):
        # Windows fix - handle read-only files in .git folder
        def handle_remove_readonly(func, path, exc):
            os.chmod(path, 0o777)
            func(path)
        shutil.rmtree(target_dir, onerror=handle_remove_readonly)
    subprocess.run(["git", "clone", "--depth=1", repo_url, target_dir], check=True)
    print(f"cloned {repo_url}")

def run_pipeline(repo_url):
    repo_name = repo_url.split("/")[-1].replace(".git", "")
    target_dir = f"data/cloned/{repo_name}"
    
    clone_repo(repo_url, target_dir)
    functions, features = analyze_repo(target_dir)
    
    print(f"found {len(functions)} functions")
    save_repo(repo_name, functions, features)
    
    def handle_remove_readonly(func, path, exc):
        os.chmod(path, 0o777)
        func(path)
    shutil.rmtree(target_dir, onerror=handle_remove_readonly)
    print("done")
    
if __name__ == "__main__":
    run_pipeline("https://github.com/pallets/flask.git")