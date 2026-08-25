# 1. Check if git is initialized
if (-Not (Test-Path ".git")) {
    Write-Host "Initializing Git repository..." -ForegroundColor Cyan
    git init
}

# 2. Check if remote origin exists
$remoteExists = $false
try {
    $null = git remote get-url origin 2>&1
    $remoteExists = $true
} catch {
    $remoteExists = $false
}

if (-Not $remoteExists) {
    $github_username = Read-Host "Enter your GitHub username"
    $repo_name = Read-Host "Enter your GitHub repository name"
    git remote add origin "https://github.com/$github_username/$repo_name.git"
    Write-Host "Remote 'origin' added." -ForegroundColor Green
} else {
    Write-Host "Remote 'origin' already exists." -ForegroundColor Cyan
}

# 3. Stage all files
Write-Host "Staging files..." -ForegroundColor Cyan
git add .

# 4. Commit with a detailed message
Write-Host "Committing files..." -ForegroundColor Cyan
git commit -m "chore(phase1): Complete Project Skeleton, Documentation, and Architecture Design"

# 5. Push to origin main
Write-Host "Pushing to GitHub..." -ForegroundColor Cyan
git branch -M main
git push -u origin main

# 6. Print the GitHub repo URL
$remote_url = git remote get-url origin
Write-Host "Successfully pushed! View your repository at: $remote_url" -ForegroundColor Green
