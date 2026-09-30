# GitHub upload

This package has not been uploaded to GitHub. Use your own account and destination repository.

For a NEW EMPTY repository, open Git Bash in the extracted 2026-Y2-S1-KU-39 folder:

```bash
git init -b main
git add .
git status
git commit -m "Add executed preprocessing notebooks and group pipeline"
git remote add origin https://github.com/OWNER/REPOSITORY.git
git push -u origin main
```

Replace OWNER/REPOSITORY with the real values. Authenticate when Git requests it. If a repository already has commits, clone and integrate into it rather than overwriting history.

## Each member

After the owner grants access, clone the repository and work on a personal branch:

```bash
git clone https://github.com/OWNER/REPOSITORY.git
cd REPOSITORY
git switch -c member-IT25103754
```

Replace the example ID with your own. Review/run your notebook, make actual corrections or add interpretation, save its outputs, then commit the specific changed files:

```bash
git add notebooks/IT25103754_Model_Specific_Normalization.ipynb
git diff --cached --stat
git commit -m "Verify normalization outputs and explain input ranges"
git push -u origin member-IT25103754
```

Open a pull request into main and have another member review it. Use descriptions that match actual work. Do not fabricate prior authorship or backdate commits.

Raw data is in the full deliverable ZIP for Courseweb/Drive, but is excluded from Git by .gitignore. Keep retrieval/provenance information in data/README.md. The Colab setup can mount the full ZIP from Drive while code/notebook outputs live in GitHub.

References:
- https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github
- https://research.google.com/colaboratory/faq.html
