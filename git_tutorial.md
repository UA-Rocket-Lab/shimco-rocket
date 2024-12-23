# Git Tutorial for SHIMCO Team

---

### Cloning the Repository
To work on shimco-rocket, you need to clone the repository to your local machine. Follow these steps:

1. Copy the Repository URL:
   - Go to the shimco-rocket repository on GitHub.
   - Click the green "Code" button and copy the HTTPS or SSH URL.

2. Run the Clone Command:
   - Open your terminal and navigate to the directory where you want to store the project.
   - Use the following command to clone the repository:
     ```
     git clone <repository-url>
     ```
     Replace `<repository-url>` with the URL you copied in step 1.

3. Navigate into the Project Directory:
     ```
     cd <repository-name>
     ```
   Replace `<repository-name>` with the name of the repository folder created by the clone command.

---

## 1. Branches
Branches allow you to work on different features or fixes without affecting the main codebase.

### Basic Commands
- Check Current Branch:
    ```
    git branch
    ```

The active branch will have a `*` next to it.

- Create a New Branch:
    ```
    git branch branch-name
    ```

- Switch to an Existing Branch:
    ```
    git checkout branch-name
    ```

- Create and Switch to a New Branch in One Step:
    ```
    git checkout -b branch-name
    ```


---

## 2. Committing
Committing is a way to save a snapshot of your changes in your local repository. Commits are **local by default** until you push them to a remote repository.

### Steps to Commit Changes
1. Stage Your Changes:
 - Stage a Single File:
   ```
   git add filename
   ```
 - Stage All Changes:
   ```
   git add .
   ```

2. Make the Commit:
 - Include a concise message describing your changes:
   ```
   git commit -m "Describe your changes here"
   ```

---

## 3. Pushing
Pushing uploads your local commits to a remote repository (e.g., GitHub) to share your changes with others or back them up.

### Steps to Push Changes
1. Check Your Current Branch:
    ```
    git branch
    ```

2. Push Your Changes:
- Push for the first time and set the upstream branch:
  ```
  git push -u origin branch-name
  ```
- After setting the upstream branch, you can simply use:
  ```
  git push
  ```

### Key Terms
- `origin`: The default name for the remote repository (an alias for the repository URL).
- Tracking Branch: After the first push, Git remembers the remote branch associated with your local branch.

---

## 4. Pull Requests (PRs)
Pull requests are used to propose changes from one branch to another (e.g., from a feature branch to `main`). These must be created and reviewed on the GitHub website.

### Creating a Pull Request
1. Push your branch to GitHub.
2. Go to the Pull Requests tab in your repository and click **New Pull Request**.
3. Select:
- Base branch: The branch you want to merge into (e.g., `main`).
- Compare branch: Your feature or bugfix branch.
4. Add a title and description explaining your changes.
5. Assign reviewers and submit the pull request.

### Referencing Issues in a Pull Request
To automatically close an issue when the pull request is merged, reference it in the pull request description or commit message:
Fixes #issue-number

---

## 5. Issues
Issues are used to track tasks, bugs, enhancements, or questions about a project.

### Creating an Issue
1. Navigate to the repository on GitHub.
2. Click on the Issues tab, then **New Issue**.
3. Add:
   - Title: A brief summary of the issue.
   - Description: Detailed explanation, including steps to reproduce (for bugs) or requirements (for features).
4. Assign labels (e.g., `bug`, `enhancement`) and team members.
5. Optionally, set milestones to group related issues.

---

## 6. General Workflow Summary
1. Create a new branch for your work:
    ```
    git checkout -b feature/branch-name
    ```

2. Stage and commit your changes:
    ```
    git add . git commit -m "Describe your changes"
    ```

3. Push your branch to the remote repository:
    ```
    git push -u origin branch-name
    ```

4. Create a pull request on GitHub, referencing any relevant issues:
Fixes #issue-number

5. After review and approval, merge the pull request into the main branch.

---

With this guide, you’ll have a solid reference for effectively using Git in your projects!
