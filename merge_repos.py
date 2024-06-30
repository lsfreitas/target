import os
import git # type: ignore

def clone_repo(repo_url, repo_path):
    if not os.path.exists(repo_path):
        git.Repo.clone_from(repo_url, repo_path)
    return git.Repo(repo_path)

def fetch_latest_commit(repo):
    repo.remotes.origin.fetch()
    return repo.head.commit.hexsha

def get_last_merged_commit(repo, tag_name):
    try:
        return repo.git.describe(tag_name, tags=True)
    except git.exc.GitCommandError:
        return None

def main():
    # Replace with your actual GitHub username. Can be set as env variable
    target_repo_url = "git@github.com:lsfreitas/target.git"
    target_repo_path = "/tmp/target_repo"
    tag_name = "last-merged-commit"

    target_repo = clone_repo(target_repo_url, target_repo_path)
    print(f"Repository cloned to {target_repo_path}")

    latest_commit = fetch_latest_commit(target_repo)
    print(f"Latest commit hash: {latest_commit}")

    last_merged_commit = get_last_merged_commit(target_repo, tag_name)
    if last_merged_commit:
        print(f"Last merged commit hash: {last_merged_commit}")
    else:
        print(f"No tag '{tag_name}' found in the repository")

if __name__ == "__main__":
    main()