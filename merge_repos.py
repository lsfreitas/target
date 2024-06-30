import os
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

def main():
    # Configure Git user identity
    configure_git_identity()

    # Fetch repository URLs and branch names from environment variables
    target_repo_url = os.getenv('TARGET_REPO_URL')
    source_repo_url = os.getenv('SOURCE_REPO_URL')
    target_branch = os.getenv('TARGET_BRANCH')
    source_branch = os.getenv('SOURCE_BRANCH')

    # Validate environment variables
    if not target_repo_url or not source_repo_url or not target_branch or not source_branch:
        print("Error: TARGET_REPO_URL, SOURCE_REPO_URL, TARGET_BRANCH, and SOURCE_BRANCH environment variables must be set.")
        return

    # Define local paths for cloning repositories
    target_repo_path = "/tmp/target_repo"
    source_repo_path = "/tmp/source_repo"

    # Clone target repository
    print(f"Cloning target repository from {target_repo_url} to {target_repo_path}")
    target_repo = clone_repo(target_repo_url, target_repo_path)
    print(f"Target repository cloned to {target_repo_path}")

    # Add the source repository as a remote to the target repository using its remote URL
    if 'source_repo' not in [remote.name for remote in target_repo.remotes]:
        target_repo.create_remote('source_repo', source_repo_url)
        print(f"Added source repository as remote 'source_repo'")

    # Fetch changes from the source repository
    target_repo.remotes.source_repo.fetch()
    print(f"Fetched latest changes from source repository")

    # Checkout the target branch
    target_repo.git.checkout(target_branch)
    print(f"Checked out to branch '{target_branch}' in target repository")

    # Merge the source repository into the target repository
    try:
        target_repo.git.merge(f'source_repo/{source_branch}', allow_unrelated_histories=True)
        print(f"Successfully merged 'source_repo/{source_branch}' into '{target_branch}'")
    except git.exc.GitCommandError as e:
        print(f"Error during merge: {e.stderr}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return

    # Push the changes to the target repository
    try:
        target_repo.remotes.origin.push(refspec=f'{target_branch}:{target_branch}')
        print(f"Successfully pushed the merged changes to '{target_branch}'")
    except git.exc.GitCommandError as e:
        print(f"Error during push: {e.stderr}")
        return

    # Remove the source remote
    target_repo.delete_remote('source_repo')
    print("Removed source repository remote")

if __name__ == "__main__":
    main()
