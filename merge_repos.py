import os
import git # type: ignore

def configure_git_identity():
    user_name = os.getenv('GIT_USER_NAME')
    user_email = os.getenv('GIT_USER_EMAIL')
    os.system(f'git config --global user.name "{user_name}"')
    os.system(f'git config --global user.email "{user_email}"')

def clone_repo(repo_url, repo_path):
    if not os.path.exists(repo_path):
        return git.Repo.clone_from(repo_url, repo_path)
    else:
        return git.Repo(repo_path)

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
    source_repo_path = "/tmp/source_repo"
    branch_name = "githubaction"

    # Clone both repositories
    target_repo = clone_repo(target_repo_url, target_repo_path)
    print(f"Target repository cloned to {target_repo_path}")

    source_repo = clone_repo(source_repo_url, source_repo_path)
    print(f"Source repository cloned to {source_repo_path}")

    # Fetch the latest changes in target repo
    target_repo.git.checkout(branch_name)
    target_repo.remotes.origin.pull()

    # Add the source repository as a remote to the target repository using its local path
    if 'source_repo' not in [remote.name for remote in target_repo.remotes]:
        target_repo.create_remote('source_repo', source_repo.working_dir)
    
    target_repo.remotes.source_repo.fetch()

    # Merge the source repository into the target repository
    try:
        target_repo.git.merge('source_repo/main', allow_unrelated_histories=True)
        target_repo.git.push("origin", branch_name)
        print(f"Successfully merged 'source_repo/main' into '{branch_name}'")
    except git.exc.GitCommandError as e:
        print(f"Error during merge: {e.stderr}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return
    
if __name__ == "__main__":
    main()