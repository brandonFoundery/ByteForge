import re
import json
from collections import defaultdict
from pathlib import Path

def parse_build_output(output_text):
    """Parse build output and group errors by file"""
    errors_by_file = defaultdict(list)
    
    # Pattern to match error lines
    # Example: D:\Repository\@Founder-y\ByteForgeFrontend\project\code\Services\Security\SecurityService.cs(65,63): error CS1503: Argument 2: cannot convert from 'string' to 'System.Guid'
    error_pattern = r'([^(]+)\((\d+),(\d+)\): (error|warning) (CS\d+): (.+)'
    
    for line in output_text.split('\n'):
        match = re.match(error_pattern, line)
        if match and 'error' in match.group(4):
            file_path = match.group(1).strip()
            line_num = match.group(2)
            col_num = match.group(3)
            error_code = match.group(5)
            error_msg = match.group(6)
            
            # Convert Windows path to relative path
            if 'ByteForgeFrontend' in file_path:
                parts = file_path.split('ByteForgeFrontend')
                relative_path = 'ByteForgeFrontend' + parts[-1]
                relative_path = relative_path.replace('\\', '/')
            else:
                relative_path = file_path.replace('\\', '/')
            
            errors_by_file[relative_path].append({
                'line': int(line_num),
                'column': int(col_num),
                'code': error_code,
                'message': error_msg
            })
    
    return dict(errors_by_file)

def create_fix_prompt(file_path, errors):
    """Create a markdown file with fix instructions for a specific file"""
    prompt = f"""# Fix Build Errors for {file_path}

## Instructions

You need to fix the following build errors in the file `{file_path}`. Follow these steps:

1. Read the file to understand the current code
2. Fix each error listed below
3. Run `dotnet build` to verify all errors are fixed
4. If there are still errors, fix them and build again
5. Once the build succeeds with no errors for this file, stop

## Errors to Fix

"""
    
    for i, error in enumerate(errors, 1):
        prompt += f"""### Error {i}
- **Location**: Line {error['line']}, Column {error['column']}
- **Error Code**: {error['code']}
- **Message**: {error['message']}

"""
    
    prompt += """## Important Notes

- Focus ONLY on fixing the errors listed above
- Do not make unnecessary changes to the code
- Preserve the existing functionality while fixing the errors
- Common fixes include:
  - Adding missing using statements
  - Fixing type mismatches
  - Adding null checks for nullable reference types
  - Correcting method signatures
  - Fixing namespace issues

After fixing all errors, run the build command to verify:
```bash
cd /mnt/d/Repository/@Founder-y/ByteForgeFrontend/project/code && cmd.exe /c "dotnet build"
```

Only stop when the build succeeds with no errors for this specific file.
"""
    
    return prompt

# Read the build output
build_output = """PASTE_BUILD_OUTPUT_HERE"""

# Parse with the actual output from the previous command
import subprocess
result = subprocess.run(
    'cd /mnt/d/Repository/@Founder-y/ByteForgeFrontend/project/code && cmd.exe /c "dotnet build ByteForgeFrontend.sln"',
    shell=True,
    capture_output=True,
    text=True
)
build_output = result.stderr + result.stdout

# Parse errors
errors_by_file = parse_build_output(build_output)

# Create output directory
output_dir = Path('/mnt/d/Repository/@Founder-y/ByteForgeFrontend/build_fixes')
output_dir.mkdir(exist_ok=True)

# Generate markdown files for each file with errors
file_count = 0
for file_path, errors in errors_by_file.items():
    if errors:  # Only create files for those with errors
        file_count += 1
        # Create safe filename
        safe_filename = file_path.replace('/', '_').replace('\\', '_').replace(':', '').replace('.cs', '') + '_fixes.md'
        
        # Generate prompt
        prompt_content = create_fix_prompt(file_path, errors)
        
        # Save to file
        output_file = output_dir / safe_filename
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(prompt_content)
        
        print(f"Created: {output_file}")

print(f"\nTotal files with errors: {file_count}")
print(f"Fix prompts saved to: {output_dir}")

# Also save a summary
summary = {
    'total_files': file_count,
    'files': {file: len(errors) for file, errors in errors_by_file.items() if errors}
}

with open(output_dir / 'error_summary.json', 'w', encoding='utf-8') as f:
    json.dump(summary, f, indent=2)