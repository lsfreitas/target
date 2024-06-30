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
        repo = git.Repo(repo_path)
        repo.remotes.origin.pull()
        return repo

def main():
    # Configure Git user identity
    configure_git_identity()

    # Fetch repository URLs from environment variables
    target_repo_url = os.getenv('TARGET_REPO_URL')
    source_repo_url = os.getenv('SOURCE_REPO_URL')

    # Define local paths for cloning repositories
    target_repo_path = "/tmp/target_repo"
    source_repo_path = "/tmp/source_repo"
    branch_name = "githubaction"

    if not target_repo_url or not source_repo_url:
        print("Error: TARGET_REPO_URL and SOURCE_REPO_URL environment variables must be set.")
        return

    # Clone both repositories
    target_repo = clone_repo(target_repo_url, target_repo_path)
    print(f"Target repository cloned to {target_repo_path}")

    source_repo = clone_repo(source_repo_url, source_repo_path)
    print(f"Source repository cloned to {source_repo_path}")

    # Ensure we are on the target branch
    target_repo.git.checkout(branch_name)

    # Add the source repository as a remote to the target repository using its remote URL
    if 'source_repo' not in [remote.name for remote in target_repo.remotes]:
        target_repo.create_remote('source_repo', source_repo_url)
    
    target_repo.remotes.source_repo.fetch()

    # Merge the source repository into the target repository
    try:
        target_repo.git.merge('source_repo/main', allow_unrelated_histories=True)
        print(f"Successfully merged 'source_repo/main' into '{branch_name}'")
    except git.exc.GitCommandError as e:
        print(f"Error during merge: {e.stderr}")
        return

    # Push the changes to the target repository
    try:
        target_repo.remotes.origin.push(refspec=f'{branch_name}:{branch_name}')
        print(f"Successfully pushed the merged changes to '{branch_name}'")
    except git.exc.GitCommandError as e:
        print(f"Error during push: {e.stderr}")
        return

if __name__ == "__main__":
    main()
