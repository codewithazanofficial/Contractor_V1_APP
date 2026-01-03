# GitHub Repository Setup Instructions

## Step 1: Create Repository on GitHub

1. Go to https://github.com/new
2. Repository name: `Contractor_APP_V1`
3. Description: "Wage Management System for Contractors"
4. Select **Private** (not public)
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click "Create repository"

## Step 2: After Creating the Repository

GitHub will show you commands. Use these commands in your terminal:

```bash
git remote add origin https://github.com/YOUR_USERNAME/Contractor_APP_V1.git
git branch -M main
git push -u origin main
```

**Note:** Replace `YOUR_USERNAME` with your actual GitHub username.

## Alternative: If you need to authenticate

If you're asked for credentials:
- Use a Personal Access Token (PAT) instead of password
- Generate one at: https://github.com/settings/tokens
- Select scopes: `repo` (full control of private repositories)

