# .gitignore Updates for FY.WB.Midway

## Summary of Changes

I've enhanced the .gitignore file to comprehensively exclude Next.js build artifacts and other unnecessary files. Here's what was added:

## Enhanced Next.js Frontend Section

### Build Outputs and Cache
- `/FrontEnd/.next/` - Next.js build cache
- `/FrontEnd/out/` - Static export output directory
- `/FrontEnd/build/` - Production build directory
- `/FrontEnd/dist/` - Distribution directory
- `.swc/` - SWC compiler cache

### Testing and Development Tools
- `/FrontEnd/coverage` - Test coverage reports
- `/FrontEnd/test-results/` - Playwright test results
- `/FrontEnd/playwright-report/` - Playwright HTML reports
- `/FrontEnd/blob-report/` - Playwright blob reports
- `/FrontEnd/cypress/videos` - Cypress test videos
- `/FrontEnd/cypress/screenshots` - Cypress test screenshots
- `/FrontEnd/cypress/downloads` - Cypress downloads

### Environment and Configuration
- `/FrontEnd/.env*.local` - Local environment files
- `/FrontEnd/next-env.d.ts` - Next.js TypeScript declarations
- `/FrontEnd/*.tsbuildinfo` - TypeScript build info
- `/FrontEnd/.eslintcache` - ESLint cache
- `.prettiercache` - Prettier cache

### Storybook and Documentation
- `/FrontEnd/.out` - Storybook build output
- `/FrontEnd/.storybook-out` - Storybook static files
- `/FrontEnd/storybook-static` - Storybook static build

### PWA and Service Workers
- `**/public/sw.js` - Service worker files
- `**/public/workbox-*.js` - Workbox files
- `**/public/worker-*.js` - Web worker files
- `**/public/*.js.map` - Source map files

### Modern Build Tools
- `.turbo` - Turbo cache
- `.sentryclirc` - Sentry configuration
- `.next/analyze/` - Bundle analyzer output

## Enhanced Requirements Generation System

### Python Development
- `Requirements_Generation_System/__pycache__/` - Python cache
- `Requirements_Generation_System/*.pyc` - Python compiled files
- `Requirements_Generation_System/*.pyo` - Python optimized files
- `Requirements_Generation_System/.pytest_cache/` - Pytest cache

### Logging and Execution
- `logs/` - Claude Code execution logs
- `*.log` - General log files

## Additional Development Tools

### Cloud and Infrastructure
- `.azure/` - Azure CLI cache
- `*.tfstate*` - Terraform state files
- `.terraform/` - Terraform cache
- `.docker/` - Docker build cache
- `*.kubeconfig` - Kubernetes configuration

### IDEs and Editors
- `.vscode/settings.json` - VS Code user settings
- `.vscode/launch.json` - VS Code debug configuration
- `.idea/` - JetBrains IDEs
- `*.sublime-*` - Sublime Text files
- Various Vim and Emacs temporary files

### Operating System Files
- Comprehensive macOS files (`.DS_Store`, `.AppleDouble`, etc.)
- Windows files (`Thumbs.db`, `Desktop.ini`, etc.)
- Linux temporary files

### Backup and Archive Files
- `*.bak`, `*.backup`, `*.orig` - Backup files
- `*.zip`, `*.tar`, `*.rar` - Archive files (unless specifically needed)
- `*.swp`, `*.swo`, `*~` - Editor swap/temporary files

### Media Files
- Large video files (`*.mp4`, `*.avi`, `*.mov`, etc.)
- These are excluded to prevent accidentally committing large media files

## Key Benefits

1. **Prevents /out Directory Commits**: The `/FrontEnd/out/` pattern specifically excludes Next.js static export output
2. **Comprehensive Build Artifact Exclusion**: All Next.js build outputs are properly ignored
3. **Development Tool Support**: Covers modern development tools like Playwright, Cypress, Storybook
4. **Cross-Platform Compatibility**: Handles files from Windows, macOS, and Linux
5. **Security**: Excludes sensitive configuration and environment files
6. **Performance**: Prevents large cache and build files from being tracked

## Package Manager Lock Files

The .gitignore includes commented options for package manager lock files:
```
# Package manager lock files (keep only one)
# Uncomment the ones you don't use:
# package-lock.json
# yarn.lock
# pnpm-lock.yaml
```

**Recommendation**: Keep only the lock file for your chosen package manager (npm, yarn, or pnpm) and uncomment the others to ignore them.

## Verification

To verify the .gitignore is working correctly:

1. **Check current status**: `git status` should not show unwanted files
2. **Test with build**: Run `npm run build` in FrontEnd directory, then check `git status`
3. **Test with development**: Run `npm run dev`, then check `git status`
4. **Verify /out exclusion**: Run `npm run export` (if configured), then verify `/FrontEnd/out/` is not tracked

## Notes

- The .gitignore is now comprehensive for a Next.js + ASP.NET Core project
- All major development tools and build outputs are covered
- The file maintains the existing ASP.NET Core patterns while enhancing frontend coverage
- Patterns are specific enough to avoid false positives while being comprehensive enough to catch all build artifacts

This enhanced .gitignore will ensure that your repository stays clean and only tracks source code and necessary configuration files, not build artifacts or temporary files.
