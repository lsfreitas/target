import os
import git # type: ignore

def configure_git_identity():
    user_name = os.getenv('GIT_USER_NAME')
    user_email = os.getenv('GIT_USER_EMAIL')
    os.system(f'git config --global user.name "{user_name}"')
    os.system(f'git config --global user.email "{user_email}"')

def clone_repo(repo_url, repo_path):
    if os.path.exists(repo_path):
        repo = git.Repo(repo_path)
        repo.remotes.origin.pull()
    else:
        repo = git.Repo.clone_from(repo_url, repo_path)
    return repo

def fetch_latest_commit(repo):
    repo.remotes.origin.fetch()
    return repo.head.commit.hexsha

def get_last_merged_commit(repo, tag_name):
    try:
        return repo.git.describe(tag_name, tags=True)
    except git.exc.GitCommandError:
        return None

def create_remote(repo, remote_name, remote_url):
    if remote_name not in [remote.name for remote in repo.remotes]:
        repo.create_remote(remote_name, remote_url)
    repo.remotes[remote_name].fetch()

def merge_source_into_target(target_repo, remote_name, branch_name):
    try:
        print("Attempting to merge...")
        target_repo.git.merge(f"{remote_name}/main", allow_unrelated_histories=True)
        target_repo.git.push("origin", branch_name)
        print(f"Successfully merged '{remote_name}/main' into '{branch_name}'")
        return True
    except git.exc.GitCommandError as e:
        print(f"Error during merge: {e.stderr}")
        return False

def main():
    # Configure Git user identity
    configure_git_identity()

    # Target and Source repo can be set as env variable
    target_repo_url = "git@github.com:lsfreitas/target.git"
    source_repo_url = "git@github.com:lsfreitas/source.git"
    target_repo_path = "/tmp/target_repo"
    remote_name = "source_repo"
    tag_name = "last-merged-commit"
    branch_name = "githubaction"

    target_repo = clone_repo(target_repo_url, target_repo_path)
    print(f"Repository cloned to {target_repo_path}")

    latest_commit = fetch_latest_commit(target_repo)
    print(f"Latest commit hash: {latest_commit}")

    last_merged_commit = get_last_merged_commit(target_repo, tag_name)
    if last_merged_commit:
        print(f"Last merged commit hash: {last_merged_commit}")
    else:
        print(f"No tag '{tag_name}' found in the repository")
    
    create_remote(target_repo, remote_name, source_repo_url)
    print(f"Remote '{remote_name}' created and fetched")

    merge_success = merge_source_into_target(target_repo, remote_name, branch_name)
    if not merge_success:
        print(f"Failed to merge '{remote_name}/main' into '{branch_name}' due to errors. Please check the error messages above for details.")

if __name__ == "__main__":
    main()