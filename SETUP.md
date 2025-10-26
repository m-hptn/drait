# GitHub Repository Setup Instructions

After creating your GitHub repository, follow these steps to complete the setup.

> **Note for Private Repositories**: GitHub Pages is only available for public repositories (or with GitHub Pro/Team/Enterprise for private repos). The documentation workflow is configured and ready but will only deploy when the repository is made public.

## 1. Enable GitHub Pages (Public Repositories Only)

1. Go to your repository on GitHub
2. Click on **Settings** (top right)
3. In the left sidebar, click **Pages**
4. Under "Build and deployment":
   - **Source**: Select "GitHub Actions"
5. Save the settings

## 2. Update README.md

Replace `YOUR_USERNAME` in [README.md](README.md) with your actual GitHub username:

```markdown
📚 **[View Live Documentation](https://YOUR_USERNAME.github.io/drait/)**
```

Change it to:
```markdown
📚 **[View Live Documentation](https://username.github.io/drait/)**
```

(Replace `username` with your actual GitHub username)

## 3. Push to GitHub

If you haven't already pushed to GitHub:

```bash
# Add the remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/drait.git

# Push to main branch
git push -u origin main
```

## 4. Verify Documentation Deployment

1. After pushing, go to the **Actions** tab in your GitHub repository
2. You should see the "Build and Deploy Documentation" workflow running
3. Wait for it to complete (green checkmark)
4. Visit `https://YOUR_USERNAME.github.io/drait/` to see your documentation

## 5. Add Status Badge (Optional)

Add a documentation build status badge to your README:

```markdown
[![Documentation](https://github.com/YOUR_USERNAME/drait/actions/workflows/docs.yml/badge.svg)](https://github.com/YOUR_USERNAME/drait/actions/workflows/docs.yml)
```

## Workflow Features

The GitHub Actions workflow ([.github/workflows/docs.yml](.github/workflows/docs.yml)) will:

- ✅ Automatically trigger on every push to `main` that changes documentation files
- ✅ Build HTML documentation using docToolchain
- ✅ Attempt to build PDF documentation (continues if it fails)
- ✅ Deploy to GitHub Pages
- ✅ Can be manually triggered via "workflow_dispatch"

## Troubleshooting

### Documentation not deploying?

1. Check the Actions tab for error messages
2. Ensure GitHub Pages is set to "GitHub Actions" as source
3. Verify the workflow file is in `.github/workflows/docs.yml`
4. Check that you pushed the workflow file to the repository

### Pages returns 404?

1. Wait a few minutes after the first deployment
2. Clear your browser cache
3. Verify the workflow completed successfully
4. Check that the Pages URL matches your GitHub username

### Want to trigger a rebuild manually?

1. Go to **Actions** tab
2. Select "Build and Deploy Documentation"
3. Click "Run workflow" button
4. Select the `main` branch
5. Click "Run workflow"

## Next Steps

Once your documentation is deployed:

1. Share the documentation URL with your team
2. Update documentation by editing files in `docs/arc42/src/docs/`
3. Push changes to `main` - documentation will auto-update
4. Consider adding more workflows for testing, linting, etc.
