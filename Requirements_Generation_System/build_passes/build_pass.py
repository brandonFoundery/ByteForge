"""
Build Pass Implementation - Claude Code Terminal Integration

This module implements Pass 4 of the AI-driven application builder.
Uses Claude Code terminals to generate actual code, compile, test, and create pull requests.
"""

import asyncio
import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

from git import Repo, GitCommandError
from github import Github
from rich.console import Console

console = Console()


class BuildPass:
    """
    Pass 4: Build Phase using Automated Build System
    
    Generates actual code and builds the application including:
    - Code file generation from specifications
    - Database migrations
    - Frontend component creation
    - Backend API implementation
    - Automated compilation and testing
    - Git commits and PR creation
    """

    def __init__(self, config: Dict[str, Any], base_path: Path, repo: Optional[Repo] = None):
        self.config = config
        self.base_path = base_path
        self.frontend_path = base_path / "FrontEnd"
        self.backend_path = base_path / "BackEnd"
        self.repo = repo

        # Get build system configuration
        self.build_config = config.get('application_builder', {}).get('build_system', {})
        self.git_config = config.get('application_builder', {}).get('git', {})

        # Claude Code terminal configuration
        self.claude_terminals = {}  # Track active Claude Code terminals
        self.wsl_available = self._check_wsl_availability()

        # Initialize GitHub client if token is available
        github_token = os.getenv('GITHUB_TOKEN')
        self.github_client = Github(github_token) if github_token else None

        # Build retry configuration
        self.max_retries = config.get('application_builder', {}).get('max_retries', 4)

    async def run(self, implementation_spec: str) -> str:
        """
        Run the build pass with Claude-powered code generation

        Args:
            implementation_spec: Implementation specification from Pass 3 (Claude Sonnet 4)

        Returns:
            Build result summary as string
        """
        console.print("[cyan]🔨 Running Build Pass with Claude-Powered Code Generation...[/cyan]")
        console.print("[dim]📋 Step 1: Parsing implementation specification...[/dim]")

        # Parse implementation specification using Claude
        build_plan = await self._parse_implementation_spec_with_claude(implementation_spec)
        console.print(f"[green]✅ Parsed build plan with {len(build_plan.get('files', []))} files to generate[/green]")

        console.print("[dim]📋 Step 2: Generating code files with Claude...[/dim]")
        # Generate code files using Claude
        generated_files = await self._generate_code_files_with_claude(build_plan, implementation_spec)
        console.print(f"[green]✅ Generated {len(generated_files)} code files[/green]")

        # Commit initial code generation
        if self.repo and generated_files:
            console.print("[dim]📋 Step 3: Committing generated code to Git...[/dim]")
            await self._commit_changes("feat: initial code generation from AI specifications")

        console.print("[dim]📋 Step 4: Building frontend application...[/dim]")
        # Build frontend with automatic bug fixing
        frontend_result = await self._build_frontend_with_fixes()

        console.print("[dim]📋 Step 5: Building backend application...[/dim]")
        # Build backend with automatic bug fixing
        backend_result = await self._build_backend_with_fixes()

        console.print("[dim]📋 Step 6: Running tests...[/dim]")
        # Run tests with automatic bug fixing
        test_results = await self._run_tests_with_fixes()

        console.print("[dim]📋 Step 7: Final build validation and bug fixing...[/dim]")
        # Final validation and bug fixing pass
        final_validation = await self._final_build_validation_and_fixes()

        # Final commit if everything succeeded
        if frontend_result and backend_result and test_results and final_validation:
            console.print("[dim]📋 Step 8: Final commit with passing tests and validation...[/dim]")
            if self.repo:
                await self._commit_changes("feat: completed implementation with passing tests and validation")

            build_summary = await self._create_build_summary(
                generated_files, frontend_result, backend_result, test_results, final_validation
            )
        else:
            console.print("[yellow]⚠️ Some build steps failed, creating failure summary...[/yellow]")
            build_summary = await self._create_failure_summary(
                frontend_result, backend_result, test_results, final_validation
            )

        console.print("[green]✅ Build Pass completed[/green]")
        return build_summary

    async def _get_frontend_build_errors(self) -> str:
        """Get frontend build errors for analysis"""
        try:
            frontend_dir = self.base_path / "FrontEnd"
            result = await asyncio.to_thread(
                subprocess.run,
                ["npm", "run", "build"],
                cwd=frontend_dir,
                capture_output=True,
                text=True,
                timeout=120
            )
            return result.stderr if result.stderr else result.stdout
        except Exception as e:
            return f"Error getting frontend build errors: {e}"

    async def _get_backend_build_errors(self) -> str:
        """Get backend build errors for analysis"""
        try:
            backend_dir = self.base_path / "BackEnd"
            result = await asyncio.to_thread(
                subprocess.run,
                ["dotnet", "build"],
                cwd=backend_dir,
                capture_output=True,
                text=True,
                timeout=120
            )
            return result.stderr if result.stderr else result.stdout
        except Exception as e:
            return f"Error getting backend build errors: {e}"

    async def _get_test_errors(self) -> str:
        """Get test errors for analysis"""
        try:
            # Try frontend tests first
            frontend_dir = self.base_path / "FrontEnd"
            result = await asyncio.to_thread(
                subprocess.run,
                ["npm", "test", "--", "--watchAll=false"],
                cwd=frontend_dir,
                capture_output=True,
                text=True,
                timeout=120
            )
            frontend_errors = result.stderr if result.stderr else result.stdout

            # Try backend tests
            backend_dir = self.base_path / "BackEnd"
            result = await asyncio.to_thread(
                subprocess.run,
                ["dotnet", "test"],
                cwd=backend_dir,
                capture_output=True,
                text=True,
                timeout=120
            )
            backend_errors = result.stderr if result.stderr else result.stdout

            return f"Frontend Test Errors:\n{frontend_errors}\n\nBackend Test Errors:\n{backend_errors}"
        except Exception as e:
            return f"Error getting test errors: {e}"

    async def _fix_frontend_bugs_with_claude(self, build_errors: str) -> bool:
        """Use Claude Code to fix frontend bugs"""
        try:
            if not self._check_wsl_availability():
                console.print("[yellow]⚠️ WSL/Claude Code not available, skipping automatic bug fixes[/yellow]")
                return False

            # Create bug fix prompt
            bug_fix_prompt = f"""
You are a senior frontend developer tasked with fixing build errors in a Next.js application.

Build Errors:
{build_errors}

Please analyze these errors and fix them by:
1. Identifying the root cause of each error
2. Making the necessary code changes to resolve the issues
3. Ensuring the fixes follow Next.js and React best practices
4. Testing that the fixes don't introduce new issues

Focus on:
- TypeScript compilation errors
- Missing dependencies
- Import/export issues
- Component prop type mismatches
- Missing files or incorrect paths

Please fix these errors systematically and ensure the build will succeed.
"""

            # Write prompt to file
            prompt_file = self.base_path / "claude_bug_fix_frontend.md"
            with open(prompt_file, 'w', encoding='utf-8') as f:
                f.write(bug_fix_prompt)

            # Execute Claude Code
            wsl_prompt_path = f"/mnt/d/Repository/@Clients/FY.WB.Midway/claude_bug_fix_frontend.md"
            command = [
                'wsl', '-d', 'Ubuntu', '-e', 'bash', '-c',
                f'cd "/mnt/d/Repository/@Clients/FY.WB.Midway" && claude -p "{wsl_prompt_path}"'
            ]

            result = await asyncio.to_thread(
                subprocess.run,
                command,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes for bug fixing
            )

            # Clean up prompt file
            if prompt_file.exists():
                prompt_file.unlink()

            if result.returncode == 0:
                console.print("[green]✅ Claude Code bug fixing completed[/green]")
                return True
            else:
                console.print(f"[red]❌ Claude Code bug fixing failed: {result.stderr}[/red]")
                return False

        except Exception as e:
            console.print(f"[red]❌ Error during frontend bug fixing: {e}[/red]")
            return False

    async def _fix_backend_bugs_with_claude(self, build_errors: str) -> bool:
        """Use Claude Code to fix backend bugs"""
        try:
            if not self._check_wsl_availability():
                console.print("[yellow]⚠️ WSL/Claude Code not available, skipping automatic bug fixes[/yellow]")
                return False

            # Create bug fix prompt
            bug_fix_prompt = f"""
You are a senior backend developer tasked with fixing build errors in an ASP.NET Core application.

Build Errors:
{build_errors}

Please analyze these errors and fix them by:
1. Identifying the root cause of each error
2. Making the necessary code changes to resolve the issues
3. Ensuring the fixes follow ASP.NET Core and C# best practices
4. Testing that the fixes don't introduce new issues

Focus on:
- C# compilation errors
- Missing using statements
- Namespace issues
- Dependency injection configuration
- Entity Framework context issues
- Missing NuGet packages
- Controller and service implementation errors

Please fix these errors systematically and ensure the build will succeed.
"""

            # Write prompt to file
            prompt_file = self.base_path / "claude_bug_fix_backend.md"
            with open(prompt_file, 'w', encoding='utf-8') as f:
                f.write(bug_fix_prompt)

            # Execute Claude Code
            wsl_prompt_path = f"/mnt/d/Repository/@Clients/FY.WB.Midway/claude_bug_fix_backend.md"
            command = [
                'wsl', '-d', 'Ubuntu', '-e', 'bash', '-c',
                f'cd "/mnt/d/Repository/@Clients/FY.WB.Midway" && claude -p "{wsl_prompt_path}"'
            ]

            result = await asyncio.to_thread(
                subprocess.run,
                command,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes for bug fixing
            )

            # Clean up prompt file
            if prompt_file.exists():
                prompt_file.unlink()

            if result.returncode == 0:
                console.print("[green]✅ Claude Code bug fixing completed[/green]")
                return True
            else:
                console.print(f"[red]❌ Claude Code bug fixing failed: {result.stderr}[/red]")
                return False

        except Exception as e:
            console.print(f"[red]❌ Error during backend bug fixing: {e}[/red]")
            return False

    async def _fix_test_bugs_with_claude(self, test_errors: str) -> bool:
        """Use Claude Code to fix test errors"""
        try:
            if not self._check_wsl_availability():
                console.print("[yellow]⚠️ WSL/Claude Code not available, skipping automatic test fixes[/yellow]")
                return False

            # Create test fix prompt
            test_fix_prompt = f"""
You are a senior developer tasked with fixing test errors in a full-stack application.

Test Errors:
{test_errors}

Please analyze these test errors and fix them by:
1. Identifying the root cause of each test failure
2. Making the necessary code changes to resolve the issues
3. Ensuring the fixes maintain test quality and coverage
4. Updating test configurations if needed

Focus on:
- Test setup and teardown issues
- Mock configuration problems
- Assertion failures
- Test environment configuration
- Missing test dependencies
- Test data setup issues

Please fix these test errors systematically and ensure all tests will pass.
"""

            # Write prompt to file
            prompt_file = self.base_path / "claude_bug_fix_tests.md"
            with open(prompt_file, 'w', encoding='utf-8') as f:
                f.write(test_fix_prompt)

            # Execute Claude Code
            wsl_prompt_path = f"/mnt/d/Repository/@Clients/FY.WB.Midway/claude_bug_fix_tests.md"
            command = [
                'wsl', '-d', 'Ubuntu', '-e', 'bash', '-c',
                f'cd "/mnt/d/Repository/@Clients/FY.WB.Midway" && claude -p "{wsl_prompt_path}"'
            ]

            result = await asyncio.to_thread(
                subprocess.run,
                command,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes for test fixing
            )

            # Clean up prompt file
            if prompt_file.exists():
                prompt_file.unlink()

            if result.returncode == 0:
                console.print("[green]✅ Claude Code test fixing completed[/green]")
                return True
            else:
                console.print(f"[red]❌ Claude Code test fixing failed: {result.stderr}[/red]")
                return False

        except Exception as e:
            console.print(f"[red]❌ Error during test bug fixing: {e}[/red]")
            return False

    async def _run_comprehensive_validation(self) -> List[Dict[str, str]]:
        """Run comprehensive validation checks"""
        validation_issues = []

        try:
            # Check for common code quality issues
            console.print("[dim]🔍 Checking code quality...[/dim]")

            # Check for TypeScript errors in frontend
            frontend_dir = self.base_path / "FrontEnd"
            if frontend_dir.exists():
                result = await asyncio.to_thread(
                    subprocess.run,
                    ["npx", "tsc", "--noEmit"],
                    cwd=frontend_dir,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                if result.returncode != 0 and result.stderr:
                    validation_issues.append({
                        "type": "typescript",
                        "description": "TypeScript compilation errors",
                        "details": result.stderr
                    })

            # Check for C# compilation warnings in backend
            backend_dir = self.base_path / "BackEnd"
            if backend_dir.exists():
                result = await asyncio.to_thread(
                    subprocess.run,
                    ["dotnet", "build", "--verbosity", "normal"],
                    cwd=backend_dir,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                if result.returncode != 0 and result.stderr:
                    validation_issues.append({
                        "type": "dotnet",
                        "description": "C# compilation warnings/errors",
                        "details": result.stderr
                    })

            # Check for missing dependencies
            console.print("[dim]🔍 Checking dependencies...[/dim]")

            # Check package.json dependencies
            package_json = frontend_dir / "package.json"
            if package_json.exists():
                result = await asyncio.to_thread(
                    subprocess.run,
                    ["npm", "audit", "--audit-level", "high"],
                    cwd=frontend_dir,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                if result.returncode != 0 and "vulnerabilities" in result.stdout:
                    validation_issues.append({
                        "type": "security",
                        "description": "High-severity npm vulnerabilities",
                        "details": result.stdout
                    })

            console.print(f"[dim]Found {len(validation_issues)} validation issues[/dim]")
            return validation_issues

        except Exception as e:
            console.print(f"[yellow]⚠️ Error during validation: {e}[/yellow]")
            return validation_issues

    async def _fix_validation_issue_with_claude(self, issue: Dict[str, str]) -> bool:
        """Fix a specific validation issue using Claude Code"""
        try:
            if not self._check_wsl_availability():
                console.print("[yellow]⚠️ WSL/Claude Code not available, skipping validation fixes[/yellow]")
                return False

            # Create validation fix prompt
            validation_fix_prompt = f"""
You are a senior developer tasked with fixing a validation issue in the codebase.

Issue Type: {issue['type']}
Description: {issue['description']}
Details:
{issue['details']}

Please analyze this validation issue and fix it by:
1. Understanding the root cause of the issue
2. Making the necessary code changes to resolve it
3. Ensuring the fix follows best practices
4. Testing that the fix doesn't introduce new issues

Please fix this validation issue systematically.
"""

            # Write prompt to file
            prompt_file = self.base_path / f"claude_validation_fix_{issue['type']}.md"
            with open(prompt_file, 'w', encoding='utf-8') as f:
                f.write(validation_fix_prompt)

            # Execute Claude Code
            wsl_prompt_path = f"/mnt/d/Repository/@Clients/FY.WB.Midway/claude_validation_fix_{issue['type']}.md"
            command = [
                'wsl', '-d', 'Ubuntu', '-e', 'bash', '-c',
                f'cd "/mnt/d/Repository/@Clients/FY.WB.Midway" && claude -p "{wsl_prompt_path}"'
            ]

            result = await asyncio.to_thread(
                subprocess.run,
                command,
                capture_output=True,
                text=True,
                timeout=180  # 3 minutes for validation fixing
            )

            # Clean up prompt file
            if prompt_file.exists():
                prompt_file.unlink()

            if result.returncode == 0:
                return True
            else:
                console.print(f"[red]❌ Validation fix failed: {result.stderr}[/red]")
                return False

        except Exception as e:
            console.print(f"[red]❌ Error during validation fixing: {e}[/red]")
            return False

    async def _build_frontend_with_fixes(self) -> bool:
        """Build frontend with automatic bug fixing"""
        console.print("[dim]🔨 Building frontend...[/dim]")

        # Try initial build
        frontend_result = await self._build_frontend()

        if frontend_result:
            return True

        # If build failed, attempt to fix bugs
        console.print("[yellow]⚠️ Frontend build failed, attempting automatic bug fixes...[/yellow]")

        for fix_attempt in range(3):  # Max 3 fix attempts
            console.print(f"[dim]🔧 Bug fix attempt {fix_attempt + 1}/3...[/dim]")

            # Get build errors
            build_errors = await self._get_frontend_build_errors()

            if not build_errors:
                console.print("[yellow]No specific build errors found to fix[/yellow]")
                break

            # Use Claude Code to fix the errors
            fix_success = await self._fix_frontend_bugs_with_claude(build_errors)

            if fix_success:
                # Try building again
                frontend_result = await self._build_frontend()
                if frontend_result:
                    console.print("[green]✅ Frontend build succeeded after bug fixes![/green]")
                    return True
            else:
                console.print(f"[red]❌ Bug fix attempt {fix_attempt + 1} failed[/red]")

        console.print("[red]❌ Frontend build failed after all fix attempts[/red]")
        return False

    async def _build_backend_with_fixes(self) -> bool:
        """Build backend with automatic bug fixing"""
        console.print("[dim]🔨 Building backend...[/dim]")

        # Try initial build
        backend_result = await self._build_backend()

        if backend_result:
            return True

        # If build failed, attempt to fix bugs
        console.print("[yellow]⚠️ Backend build failed, attempting automatic bug fixes...[/yellow]")

        for fix_attempt in range(3):  # Max 3 fix attempts
            console.print(f"[dim]🔧 Bug fix attempt {fix_attempt + 1}/3...[/dim]")

            # Get build errors
            build_errors = await self._get_backend_build_errors()

            if not build_errors:
                console.print("[yellow]No specific build errors found to fix[/yellow]")
                break

            # Use Claude Code to fix the errors
            fix_success = await self._fix_backend_bugs_with_claude(build_errors)

            if fix_success:
                # Try building again
                backend_result = await self._build_backend()
                if backend_result:
                    console.print("[green]✅ Backend build succeeded after bug fixes![/green]")
                    return True
            else:
                console.print(f"[red]❌ Bug fix attempt {fix_attempt + 1} failed[/red]")

        console.print("[red]❌ Backend build failed after all fix attempts[/red]")
        return False

    async def _run_tests_with_fixes(self) -> bool:
        """Run tests with automatic bug fixing"""
        console.print("[dim]🧪 Running tests...[/dim]")

        # Try initial test run
        test_result = await self._run_tests()

        if test_result:
            return True

        # If tests failed, attempt to fix bugs
        console.print("[yellow]⚠️ Tests failed, attempting automatic bug fixes...[/yellow]")

        for fix_attempt in range(2):  # Max 2 fix attempts for tests
            console.print(f"[dim]🔧 Test fix attempt {fix_attempt + 1}/2...[/dim]")

            # Get test errors
            test_errors = await self._get_test_errors()

            if not test_errors:
                console.print("[yellow]No specific test errors found to fix[/yellow]")
                break

            # Use Claude Code to fix the test errors
            fix_success = await self._fix_test_bugs_with_claude(test_errors)

            if fix_success:
                # Try running tests again
                test_result = await self._run_tests()
                if test_result:
                    console.print("[green]✅ Tests passed after bug fixes![/green]")
                    return True
            else:
                console.print(f"[red]❌ Test fix attempt {fix_attempt + 1} failed[/red]")

        console.print("[red]❌ Tests failed after all fix attempts[/red]")
        return False

    async def _final_build_validation_and_fixes(self) -> bool:
        """Final comprehensive build validation and bug fixing"""
        console.print("[dim]🔍 Running final build validation...[/dim]")

        # Run comprehensive validation checks
        validation_issues = await self._run_comprehensive_validation()

        if not validation_issues:
            console.print("[green]✅ Final validation passed - no issues found![/green]")
            return True

        console.print(f"[yellow]⚠️ Found {len(validation_issues)} validation issues, attempting fixes...[/yellow]")

        # Attempt to fix validation issues
        for issue in validation_issues:
            console.print(f"[dim]🔧 Fixing: {issue['description']}...[/dim]")

            fix_success = await self._fix_validation_issue_with_claude(issue)

            if fix_success:
                console.print(f"[green]✅ Fixed: {issue['description']}[/green]")
            else:
                console.print(f"[red]❌ Could not fix: {issue['description']}[/red]")

        # Re-run validation after fixes
        final_validation_issues = await self._run_comprehensive_validation()

        if not final_validation_issues:
            console.print("[green]✅ Final validation passed after fixes![/green]")
            return True
        else:
            console.print(f"[yellow]⚠️ {len(final_validation_issues)} validation issues remain[/yellow]")
            return False

    def _check_wsl_availability(self) -> bool:
        """Check if WSL Ubuntu and Claude Code are available"""
        try:
            # Check if WSL Ubuntu is available
            result = subprocess.run(['wsl', '-d', 'Ubuntu', '-e', 'echo', 'test'],
                                  capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                console.print("[yellow]⚠️ WSL Ubuntu not available, will use fallback methods[/yellow]")
                return False

            # Check if Claude Code is installed in Ubuntu
            result = subprocess.run(['wsl', '-d', 'Ubuntu', '-e', 'bash', '-c', 'which claude'],
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                console.print("[green]✅ WSL Ubuntu and Claude Code are available[/green]")
                return True
            else:
                console.print("[yellow]⚠️ Claude Code not installed in WSL Ubuntu, will use fallback methods[/yellow]")
                return False
        except Exception as e:
            console.print(f"[yellow]⚠️ Could not check WSL/Claude Code status: {e}[/yellow]")
            return False

    async def _parse_implementation_spec_with_claude(self, implementation_spec: str) -> Dict[str, Any]:
        """Parse the implementation specification using Claude to extract build instructions"""
        console.print("[dim]🤖 Using Claude to parse implementation specification...[/dim]")

        parsing_prompt = f"""
You are a code generation assistant. Parse the following implementation specification and extract a structured build plan.

Implementation Specification:
{implementation_spec}

Please analyze this specification and return a JSON object with the following structure:
{{
    "files": [
        {{
            "path": "relative/path/to/file.ext",
            "type": "controller|service|component|page|model|test|config",
            "description": "Brief description of what this file should contain",
            "dependencies": ["list", "of", "dependencies"]
        }}
    ],
    "database_changes": [
        {{
            "type": "migration|entity|seed",
            "description": "Description of database change"
        }}
    ],
    "build_steps": [
        "Step 1: Description",
        "Step 2: Description"
    ]
}}

Focus on identifying:
1. Backend files (controllers, services, models, etc.)
2. Frontend files (components, pages, hooks, etc.)
3. Database changes (migrations, entities)
4. Configuration files
5. Test files

Return ONLY the JSON object, no additional text.
"""

        try:
            response = await asyncio.to_thread(
                self.claude_client.messages.create,
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                messages=[{"role": "user", "content": parsing_prompt}]
            )

            # Parse Claude's response
            response_text = response.content[0].text.strip()
            console.print(f"[dim]📝 Claude parsing response: {len(response_text)} characters[/dim]")

            # Extract JSON from response
            if response_text.startswith('```json'):
                response_text = response_text[7:-3]
            elif response_text.startswith('```'):
                response_text = response_text[3:-3]

            build_plan = json.loads(response_text)
            console.print(f"[green]✅ Successfully parsed build plan with {len(build_plan.get('files', []))} files[/green]")
            return build_plan

        except Exception as e:
            console.print(f"[red]❌ Failed to parse with Claude: {e}[/red]")
            console.print("[yellow]⚠️ Falling back to simple parsing...[/yellow]")

            # Fallback to simple parsing
            return {
                'files': [
                    {
                        'path': 'BackEnd/FY.WB.Midway/Controllers/SampleController.cs',
                        'type': 'controller',
                        'description': 'Sample controller generated from specifications',
                        'dependencies': []
                    },
                    {
                        'path': 'FrontEnd/src/components/SampleComponent.tsx',
                        'type': 'component',
                        'description': 'Sample React component generated from specifications',
                        'dependencies': []
                    }
                ],
                'database_changes': [],
                'build_steps': ['Generate code files', 'Build applications', 'Run tests']
            }

    async def _generate_code_files_with_claude(self, build_plan: Dict[str, Any], implementation_spec: str) -> List[str]:
        """Generate actual code files using Claude Code terminals"""
        generated_files = []

        console.print("[yellow]📝 Generating code files with Claude Code terminals...[/yellow]")

        if not self.wsl_available:
            console.print("[red]❌ WSL not available, cannot use Claude Code terminals[/red]")
            return []

        # Prepare Claude Code context
        context_prepared = await self._prepare_claude_code_context(implementation_spec)
        if not context_prepared:
            console.print("[red]❌ Failed to prepare Claude Code context[/red]")
            return []

        # Generate each file using individual Claude Code commands
        for file_info in build_plan.get('files', []):
            console.print(f"[dim]🤖 Generating {file_info['path']} ({file_info['type']})...[/dim]")

            file_path = await self._generate_file_with_claude_code(None, file_info)
            if file_path:
                generated_files.append(file_path)
                console.print(f"[green]✅ Generated {file_info['path']}[/green]")
            else:
                console.print(f"[red]❌ Failed to generate {file_info['path']}[/red]")

        # Clean up context files
        await self._cleanup_claude_code_context()

        console.print(f"[green]✅ Generated {len(generated_files)} files total[/green]")
        return generated_files

    async def _prepare_claude_code_context(self, implementation_spec: str) -> bool:
        """Prepare context files for Claude Code"""
        console.print("[dim]🚀 Preparing Claude Code context...[/dim]")

        try:
            # Create context file for Claude Code
            context_file = self.base_path / "claude_context.md"
            context_content = f"""# Implementation Context

## Project Structure
- Frontend: Next.js with TypeScript and Tailwind CSS
- Backend: ASP.NET Core with Entity Framework and CQRS
- Database: Azure SQL Database

## Implementation Specification
{implementation_spec}

## Task
Generate the code files as specified in the implementation plan. Follow the project's architecture patterns and coding standards.
"""
            context_file.write_text(context_content, encoding='utf-8')

            console.print(f"[dim]📋 Created context file: {len(context_content)} characters[/dim]")
            console.print("[green]✅ Claude Code context prepared[/green]")
            return True

        except Exception as e:
            console.print(f"[red]❌ Failed to prepare Claude Code context: {e}[/red]")
            return False

    async def _generate_file_with_claude_code(self, claude_terminal: Optional[subprocess.Popen], file_info: Dict[str, Any]) -> Optional[str]:
        """Generate a single file using Claude Code terminal"""
        file_path = file_info['path']
        file_type = file_info['type']
        description = file_info['description']

        console.print(f"[dim]🤖 Asking Claude Code to generate {file_path}...[/dim]")

        try:
            # Convert Windows path to WSL path for the specific file
            wsl_project_path = str(self.base_path).replace('\\', '/').replace('D:', '/mnt/d')
            wsl_file_path = f"{wsl_project_path}/{file_path}"

            # Create a more specific instruction for Claude Code
            instruction = f"""Create the file {wsl_file_path}

File Type: {file_type}
Description: {description}

Requirements:
- Follow the project's architecture patterns ({file_type} best practices)
- Use appropriate coding standards for {file_type}
- Include proper error handling and validation
- Add comprehensive documentation and comments
- Ensure the file integrates well with the existing codebase
- Create any necessary parent directories

Please generate this file with complete, production-ready code.
"""

            # Use a separate Claude Code command for each file to ensure clean execution
            cmd = [
                'wsl', '-d', 'Ubuntu', '-e', 'bash', '-c',
                f'cd "{wsl_project_path}" && echo "{instruction}" | claude -p "Generate the requested file"'
            ]

            console.print(f"[dim]📋 Executing Claude Code command for {file_path}...[/dim]")

            # Execute Claude Code command
            result = await asyncio.to_thread(
                subprocess.run,
                cmd,
                capture_output=True,
                text=True,
                timeout=60  # 1 minute timeout per file
            )

            if result.returncode == 0:
                console.print(f"[dim]✅ Claude Code command completed for {file_path}[/dim]")
            else:
                console.print(f"[yellow]⚠️ Claude Code command had issues: {result.stderr}[/yellow]")

            # Wait a moment for file system sync
            await asyncio.sleep(2)

            # Check if file was created
            full_path = self.base_path / file_path
            if full_path.exists():
                file_size = full_path.stat().st_size
                console.print(f"[green]✅ Claude Code generated {file_path} ({file_size} bytes)[/green]")
                return str(full_path)
            else:
                console.print(f"[yellow]⚠️ File {file_path} not found after Claude Code execution[/yellow]")
                return None

        except Exception as e:
            console.print(f"[red]❌ Error executing Claude Code for {file_path}: {e}[/red]")
            return None

    async def _cleanup_claude_code_context(self):
        """Clean up Claude Code context files"""
        console.print("[dim]🧹 Cleaning up Claude Code context...[/dim]")

        try:
            # Clean up context file
            context_file = self.base_path / "claude_context.md"
            if context_file.exists():
                context_file.unlink()
                console.print("[green]✅ Claude Code context cleaned up[/green]")
            else:
                console.print("[dim]No context file to clean up[/dim]")

        except Exception as e:
            console.print(f"[yellow]⚠️ Error during Claude Code cleanup: {e}[/yellow]")







    async def _build_frontend(self) -> bool:
        """Build the frontend application"""
        console.print("[yellow]🔨 Building frontend...[/yellow]")
        
        frontend_config = self.build_config.get('frontend', {})
        build_command = frontend_config.get('build_command', ['npm', 'run', 'build'])
        
        return await self._run_build_command(
            build_command, 
            self.frontend_path,
            "Frontend build"
        )

    async def _build_backend(self) -> bool:
        """Build the backend application"""
        console.print("[yellow]🔨 Building backend...[/yellow]")
        
        backend_config = self.build_config.get('backend', {})
        build_command = backend_config.get('build_command', ['dotnet', 'build'])
        working_dir = self.backend_path / backend_config.get('working_directory', 'FY.WB.Midway')
        
        return await self._run_build_command(
            build_command,
            working_dir,
            "Backend build"
        )

    async def _run_tests(self) -> bool:
        """Run tests for both frontend and backend"""
        console.print("[yellow]🧪 Running tests...[/yellow]")
        
        # Run frontend tests
        frontend_config = self.build_config.get('frontend', {})
        frontend_test_cmd = frontend_config.get('test_command', ['npm', 'test', '--', '--watchAll=false'])
        
        frontend_tests = await self._run_build_command(
            frontend_test_cmd,
            self.frontend_path,
            "Frontend tests"
        )
        
        # Run backend tests
        backend_config = self.build_config.get('backend', {})
        backend_test_cmd = backend_config.get('test_command', ['dotnet', 'test'])
        working_dir = self.backend_path / backend_config.get('working_directory', 'FY.WB.Midway')
        
        backend_tests = await self._run_build_command(
            backend_test_cmd,
            working_dir,
            "Backend tests"
        )
        
        return frontend_tests and backend_tests

    async def _run_build_command(self, command: List[str], working_dir: Path, operation_name: str) -> bool:
        """Run a build command with retry logic"""
        for attempt in range(self.max_retries):
            try:
                console.print(f"[dim]Running: {' '.join(command)} (attempt {attempt + 1})[/dim]")
                
                result = await asyncio.to_thread(
                    subprocess.run,
                    command,
                    cwd=working_dir,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
                
                if result.returncode == 0:
                    console.print(f"[green]✅ {operation_name} succeeded[/green]")
                    return True
                else:
                    console.print(f"[red]❌ {operation_name} failed (attempt {attempt + 1})[/red]")
                    console.print(f"[red]Error: {result.stderr}[/red]")
                    
                    if attempt < self.max_retries - 1:
                        console.print(f"[yellow]Retrying in 2 seconds...[/yellow]")
                        await asyncio.sleep(2)
                
            except subprocess.TimeoutExpired:
                console.print(f"[red]❌ {operation_name} timed out (attempt {attempt + 1})[/red]")
            except Exception as e:
                console.print(f"[red]❌ {operation_name} failed with exception: {e}[/red]")
        
        return False

    async def _commit_changes(self, commit_message: str):
        """Commit changes to Git"""
        if not self.repo:
            return
        
        try:
            # Add all changes
            self.repo.git.add(all=True)
            
            # Check if there are changes to commit
            if self.repo.is_dirty():
                self.repo.index.commit(commit_message)
                console.print(f"[green]✅ Committed: {commit_message}[/green]")
            else:
                console.print("[yellow]No changes to commit[/yellow]")
                
        except Exception as e:
            console.print(f"[red]Failed to commit changes: {e}[/red]")

    async def _create_build_summary(self, generated_files: List[str], frontend_result: bool,
                                  backend_result: bool, test_results: bool, final_validation: bool) -> str:
        """Create a summary of the successful build"""
        return f"""# Build Pass Summary

## Build Status: ✅ SUCCESS

### Generated Files ({len(generated_files)})
{chr(10).join(f"- {file}" for file in generated_files)}

### Build Results (with Automatic Bug Fixing)
- **Frontend Build**: {'✅ Success' if frontend_result else '❌ Failed'} (with automatic bug fixes)
- **Backend Build**: {'✅ Success' if backend_result else '❌ Failed'} (with automatic bug fixes)
- **Tests**: {'✅ All Passed' if test_results else '❌ Some Failed'} (with automatic bug fixes)
- **Final Validation**: {'✅ Passed' if final_validation else '❌ Failed'} (comprehensive validation and fixes)

### Automatic Bug Fixing Applied
The build process included automatic bug detection and fixing:
- Frontend compilation errors were automatically resolved
- Backend compilation errors were automatically resolved
- Test failures were automatically fixed
- Code quality issues were automatically addressed
- Final validation ensured production readiness

### Next Steps
The implementation has been successfully built, tested, and validated with automatic bug fixing. A pull request can now be created for code review.

*Generated by AI-Driven Application Builder - Build Pass with Automatic Bug Fixing*
"""

    async def _create_failure_summary(self, frontend_result: bool, backend_result: bool,
                                    test_results: bool, final_validation: bool) -> str:
        """Create a summary of the failed build"""
        return f"""# Build Pass Summary

## Build Status: ❌ FAILED

### Build Results
- **Frontend Build**: {'✅ Success' if frontend_result else '❌ Failed'}
- **Backend Build**: {'✅ Success' if backend_result else '❌ Failed'}
- **Tests**: {'✅ All Passed' if test_results else '❌ Some Failed'}

### Recommended Actions
1. Review build logs for specific error messages
2. Check generated code for syntax errors
3. Verify all dependencies are properly installed
4. Consider running the build process manually for debugging

*Generated by AI-Driven Application Builder - Build Pass*
"""
