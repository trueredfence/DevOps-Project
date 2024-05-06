# DevOps Projects

- [`Ansible`](Ansible) - Ansible projects
- [`Docker`](Docker) - Docker projects
- [`Jenkins`](Jenkins) - Jenkins projets
- [`Terraform`](Terraform) - Terraform projects

## ⭐️ Show Your Support: Star This Repository! ⭐️

🌟 If you find this repository helpful, I'd greatly appreciate your support by starring it! 🚀"

## Github Commands

- [`Github`](Github) - Common used commands

## Python Script for windows/linux/mac to download selected Project folder from this repo

- Create a file with `download.py` and copy paste below script into this file.
- Execute `download.py`

```
python3 download.py
```

```python
import subprocess
import os

def downLoadFolder():
    print("Cloning Git repository...")
    subprocess.run(["git", "clone", "--filter=blob:none", "--no-checkout", gitRepo])
    repoName = os.path.basename(gitRepo[:-4])  # Removes '.git' extension
    os.chdir(repoName)
    subprocess.run(["git", "sparse-checkout", "set", "--cone"])
    print(f"Switching to {branchName} branch...")
    subprocess.run(["git", "checkout", branchName])
    subprocess.run(["git", "sparse-checkout", "set", folderPath])

def askUser():
    # Read user input for Git repository URL, repository name, folder path, and branch name
    gitRepo = input("\033[1;32mEnter git repo URL (default: https://github.com/trueredfence/DevOps.git): \033[0m") or "https://github.com/trueredfence/DevOps.git"
    folderPath = input("\033[1;32mEnter folder path to clone (default: Docker): \033[0m") or "Docker"
    branchName = input("\033[1;32mEnter branch name (default: main): \033[0m") or "main"

    # Confirm with the user before starting the cloning process
    print("\033[1;33mYou provided the following inputs:\033[0m")
    print("\033[1;33mGit repo URL:", gitRepo, "\033[0m")
    print("\033[1;33mFolder path to clone:", folderPath, "\033[0m")
    print("\033[1;33mBranch name:", branchName, "\033[0m")
    confirm = input("\033[1;32mDo you want to continue with the cloning process? (y/n): \033[0m")
    return gitRepo, folderPath, branchName, confirm

gitRepo, folderPath, branchName, confirm = askUser()

while confirm.lower() not in ['y', 'yes']:
    gitRepo, folderPath, branchName, confirm = askUser()

downLoadFolder()
```
