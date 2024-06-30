import os
import requests
import git

def configure_git_identity():
    user_name = os.getenv('GIT_USER_NAME')
    user_email = os.getenv('GIT_USER_EMAIL')
    os.system(f'git config --global user.name "{user_name}"')
    os.system(f'git config --global user.email "{user_email}"')

def clone_repo(repo_url, repo_path):
    if not os.path.exists(repo_path):
        return git.Repo.clone_from(repo_url, repo_path)
    else:
        repo = git.Repo(repo_path)
        repo.remotes.origin.pull()
        return repo

def add_remote(repo, remote_name, remote_url):
    if remote_name not in [remote.name for remote in repo.remotes]:
        repo.create_remote(remote_name, remote_url)
        print(f"Added {remote_name} as remote with URL {remote_url}")

def fetch_remote(repo, remote_name):
    repo.remotes[remote_name].fetch()
    print(f"Fetched latest changes from {remote_name}")

def checkout_branch(repo, branch_name):
    repo.git.checkout(branch_name)
    print(f"Checked out to branch '{branch_name}'")

def get_latest_commit_from_github(repo_url, branch_name, token):
    api_url = f"https://api.github.com/repos/{repo_url}/commits/{branch_name}"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(api_url, headers=headers)
    response.raise_for_status()
    return response.json()['sha']

def get_latest_commit_hash(repo, branch_name):
    return repo.git.rev_parse(f'{branch_name}')

def merge_branches(repo, source_branch, target_branch):
    try:
        repo.git.merge(source_branch, allow_unrelated_histories=True)
        print(f"Successfully merged '{source_branch}' into '{target_branch}'")
    except git.exc.GitCommandError as e:
        print(f"Error during merge: {e.stderr}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False
    return True

def push_changes(repo, branch_name):
    try:
        repo.remotes.origin.push(refspec=f'{branch_name}:{branch_name}')
        print(f"Successfully pushed the merged changes to '{branch_name}'")
    except git.exc.GitCommandError as e:
        print(f"Error during push: {e.stderr}")
        return False
    return True

def remove_remote(repo, remote_name):
    repo.delete_remote(remote_name)
    print(f"Removed remote '{remote_name}'")

def main():
    # Configure Git user identity
    configure_git_identity()

    # Fetch repository URLs and branch names from environment variables
    target_repo_url = os.getenv('TARGET_REPO_URL')
    source_repo_url = os.getenv('SOURCE_REPO_URL')
    target_branch = os.getenv('TARGET_BRANCH')
    source_branch = os.getenv('SOURCE_BRANCH')
    github_token = os.getenv('GITHUB_TOKEN')

    # Validate environment variables
    if not target_repo_url or not source_repo_url or not target_branch or not source_branch or not github_token:
        print("Error: TARGET_REPO_URL, SOURCE_REPO_URL, TARGET_BRANCH, SOURCE_BRANCH, and GITHUB_TOKEN environment variables must be set.")
        return

    # Define local paths for cloning repositories
    target_repo_path = "/tmp/target_repo"
    source_repo_path = "/tmp/source_repo"

    # Clone target repository
    target_repo = clone_repo(target_repo_url, target_repo_path)
    print(f"Target repository cloned to {target_repo_path}")

    # Add the source repository as a remote to the target repository
    add_remote(target_repo, 'source_repo', source_repo_url)

    # Fetch changes from the source repository
    fetch_remote(target_repo, 'source_repo')

    # Checkout the target branch
    checkout_branch(target_repo, target_branch)

    # Get latest commit hashes
    latest_source_commit = get_latest_commit_from_github(source_repo_url, source_branch, github_token)
    target_commit_hash = get_latest_commit_hash(target_repo, target_branch)

    # Check if there are changes in the source repository
    if target_commit_hash == latest_source_commit:
        print("No new changes to merge from source repository.")
        remove_remote(target_repo, 'source_repo')
        return

    # Merge the source repository into the target repository
    if merge_branches(target_repo, f'source_repo/{source_branch}', target_branch):
        # Push the changes to the target repository
        if push_changes(target_repo, target_branch):
            # Remove the source remote
            remove_remote(target_repo, 'source_repo')

if __name__ == "__main__":
    main()
