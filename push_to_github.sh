#!/bin/bash

# 1. Check if git is initialized
if [ ! -d ".git" ]; then
    echo "Initializing Git repository..."
    git init
fi

# 2. Check if remote origin exists
if ! git remote get-url origin > /dev/null 2>&1; then
    read -p "Enter your GitHub username: " github_username
    read -p "Enter your GitHub repository name: " repo_name
    git remote add origin "https://github.com/${github_username}/${repo_name}.git"
    echo "Remote 'origin' added."
else
    echo "Remote 'origin' already exists."
fi

# 3. Stage all files
echo "Staging files..."
git add .

# 4. Commit with a detailed message
echo "Committing files..."
git commit -m "chore(phase1): Complete Project Skeleton, Documentation, and Architecture Design"

# 5. Push to origin main
echo "Pushing to GitHub..."
# Ensure branch is main
git branch -M main
git push -u origin main

# 6. Print the GitHub repo URL
remote_url=$(git remote get-url origin)
echo "Successfully pushed! View your repository at: $remote_url"
