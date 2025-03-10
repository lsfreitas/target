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

def fetch_all(repo):
    for remote in repo.remotes:
        remote.fetch()
    print("Fetched all remotes")

def checkout_branch(repo, branch_name):
    repo.git.checkout(branch_name)
    print(f"Checked out to branch '{branch_name}'")

def create_new_branch(repo, branch_name):
    repo.git.checkout('-b', branch_name)
    print(f"Created and checked out to new branch '{branch_name}'")

def commit_merge_conflict(repo, conflict_message):
    repo.git.add(A=True)
    repo.index.commit(conflict_message)
    print("Committed merge conflict changes")

def get_commits_to_merge(repo, source_branch, target_branch):
    try:
        commits = repo.git.rev_list(f"{target_branch}..{source_branch}").split('\n')
        return [commit for commit in commits if commit]
    except git.exc.GitCommandError as e:
        print(f"Error during commit comparison: {e.stderr}")
        return []

def merge_branches(repo, source_branch, target_branch):
    try:
        repo.git.merge(source_branch, allow_unrelated_histories=True)
        print(f"Successfully merged '{source_branch}' into '{target_branch}'")
    except git.exc.GitCommandError as e:
        print(f"Error during merge: {e.stderr}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False, e.stderr
    return True, ""

def push_changes(repo, branch_name):
    try:
        repo.remotes.origin.push(refspec=f'{branch_name}:{branch_name}')
        print(f"Successfully pushed the merged changes to '{branch_name}'")
    except git.exc.GitCommandError as e:
        print(f"Error during push: {e.stderr}")
        return False
    return True

def create_pull_request(github_token, repo_url, source_branch, target_branch, conflict_details):
    repo_name = repo_url.split(":")[1].replace(".git", "")
    api_url = f"https://api.github.com/repos/{repo_name}/pulls"
    headers = {"Authorization": f"token {github_token}"}
    data = {
        "title": "Merge conflicts detected",
        "head": source_branch,
        "base": target_branch,
        "body": f"Merge conflicts detected:\n\n{conflict_details}"
    }
    response = requests.post(api_url, headers=headers, json=data)
    if response.status_code == 201:
        print(f"Pull request created successfully: {response.json()['html_url']}")
    else:
        print(f"Failed to create pull request: {response.json()}")

def remove_remote(repo, remote_name):
    repo.delete_remote(remote_name)
    print(f"Removed remote '{remote_name}'")

def check_for_existing_conflict_branch(repo, conflict_prefix="merge-conflict-"):
    branches = repo.git.branch('-r').split('\n')
    conflict_branch = None
    for branch in branches:
        branch = branch.strip()
        if branch.startswith(f'origin/{conflict_prefix}'):
            conflict_branch = branch.split('/')[-1]
            break
    return conflict_branch

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

    # Check for existing conflict branch
    existing_conflict_branch = check_for_existing_conflict_branch(target_repo)
    if existing_conflict_branch:
        print(f"Unresolved conflicts in branch {existing_conflict_branch}. Please resolve conflicts before merging.")
        return

    # Add the source repository as a remote to the target repository
    add_remote(target_repo, 'source_repo', source_repo_url)

    # Fetch all branches from both repositories
    fetch_all(target_repo)

    # Checkout the target branch
    checkout_branch(target_repo, target_branch)

    # Get the list of commits to merge
    commits_to_merge = get_commits_to_merge(target_repo, f'source_repo/{source_branch}', f'origin/{target_branch}')

    # Check if there are new changes in the source repository
    if not commits_to_merge:
        print("No new changes to merge from source repository.")
        remove_remote(target_repo, 'source_repo')
        return

    # Merge the source repository into the target repository
    merge_success, conflict_details = merge_branches(target_repo, f'source_repo/{source_branch}', target_branch)
    if not merge_success:
        # Create a new branch for the merge conflict
        conflict_branch = "merge-conflict-" + commits_to_merge[0][:7]
        create_new_branch(target_repo, conflict_branch)
        commit_merge_conflict(target_repo, "Resolve merge conflicts")
        push_changes(target_repo, conflict_branch)
        # Create a pull request with the merge conflicts
        create_pull_request(github_token, target_repo_url, conflict_branch, target_branch, conflict_details)
        remove_remote(target_repo, 'source_repo')
        return

    # Push the changes to the target repository
    if push_changes(target_repo, target_branch):
        # Remove the source remote
        remove_remote(target_repo, 'source_repo')

if __name__ == "__main__":
    main()
