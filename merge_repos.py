import os
import git # type: ignore

def clone_repo(repo_url, repo_path):
    if not os.path.exists(repo_path):
        git.Repo.clone_from(repo_url, repo_path)
    return git.Repo(repo_path)

def main():
    # Replace with your actual GitHub username
    repo_url = "git@github.com:lsfreitas/target.git"
    repo_path = "/tmp/target_repo"

    repo = clone_repo(repo_url, repo_path)
    print(f"Repository cloned to {repo_path}")

if __name__ == "__main__":
    main()