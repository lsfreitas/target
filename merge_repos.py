import os
import git # type: ignore

def clone_repo(repo_url, repo_path):
    if not os.path.exists(repo_path):
        git.Repo.clone_from(repo_url, repo_path)
    return git.Repo(repo_path)

def fetch_latest_commit(repo):
    repo.remotes.origin.fetch()
    return repo.head.commit.hexsha

def main():
    # Replace with your actual GitHub username. Can be set as env variable
    repo_url = "git@github.com:lsfreitas/target.git"
    repo_path = "/tmp/target_repo"

    repo = clone_repo(repo_url, repo_path)
    print(f"Repository cloned to {repo_path}")

    latest_commit = fetch_latest_commit(repo)
    print(f"Latest commit hash: {latest_commit}")

if __name__ == "__main__":
    main()