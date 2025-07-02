# Universal Path Structure Documentation

## Overview

This document defines the universal path structure used throughout the ByteForge Requirements Generation System to ensure consistent, cross-platform compatibility between Windows and WSL environments.

## Path Structure

### Base Definitions

```
Requirements_Generation_System/     # Script execution directory
├── ByteForge/                     # Parent directory (ByteForgePath)
    └── project/                   # ByteForgeProjectPath
        ├── design/                # Design documents
        │   ├── claude_instructions/  # Claude Code instruction files
        │   ├── backend-agent-design.md
        │   ├── frontend-agent-design.md
        │   └── ...
        ├── code/                  # Generated application code
        ├── requirements/          # Generated requirements documents
        ├── requirements_artifacts/ # Source requirements from client
        └── generation_status/     # Status tracking files
```

### Universal Path Variables

1. **ByteForgePath** = `{relative_path}\ByteForge`
   - Always the parent directory of Requirements_Generation_System
   - Cross-platform: `Path(__file__).parent.parent`

2. **ByteForgeProjectPath** = `{ByteForgePath}\project`
   - All generated content goes under this path
   - Cross-platform: `byteforge_path / "project"`

### Implementation Pattern

```python
# Universal Path Structure - Cross-platform compatible
base_path = Path(__file__).parent.resolve()  # Requirements_Generation_System (absolute)
byteforge_path = base_path.parent            # ByteForge directory
byteforge_project_path = byteforge_path / "project"  # ByteForgeProjectPath

# All generated content paths
instructions_path = byteforge_project_path / "design" / "claude_instructions"
code_output_path = byteforge_project_path / "code"
design_path = byteforge_project_path / "design"
requirements_path = byteforge_project_path / "requirements"
```

## Cross-Platform Compatibility

### Windows Paths
```
D:\Repository\ContractLogix\LSOMitigator\ByteForge\project\design\claude_instructions
```

### WSL Paths
```
/mnt/d/Repository/ContractLogix/LSOMitigator/ByteForge/project/design/claude_instructions
```

### Path Conversion Function
```python
def _get_cross_platform_path(self, path: Path, for_execution: bool = False) -> str:
    """Get cross-platform compatible path for the current execution environment"""
    if for_execution and self.needs_wsl:
        # Windows calling WSL - convert to WSL format
        return self._convert_to_wsl_path(str(path.absolute()))
    else:
        # Direct execution (WSL, Linux, or Windows native)
        return str(path.absolute())
```

## Configuration Structure

### config.yaml
```yaml
paths:
  # Universal Path Structure - ALWAYS relative to Requirements_Generation_System
  byteforge_path: ".."                           # ByteForgePath
  byteforge_project_path: "../project"           # ByteForgeProjectPath
  
  # All generated content goes under ByteForgeProjectPath
  requirements_dir: "../project/requirements_artifacts"
  output_dir: "../project/requirements"
  status_dir: "../project/generation_status"
  design_dir: "../project/design"
  code_dir: "../project/code"
  
  # Prompts stay in Requirements_Generation_System
  prompts_dir: "Requirements_Generation_Prompts"
```

## Benefits

1. **Consistency**: Same path structure works from both Windows and WSL
2. **Maintainability**: Single source of truth for all paths
3. **Cross-platform**: Automatic path conversion for different environments
4. **Predictable**: Always relative to Requirements_Generation_System directory
5. **Scalable**: Easy to add new path types following the same pattern

## Usage Guidelines

1. **Always use absolute paths** with `.resolve()` for base directory detection
2. **Use Path objects** instead of string concatenation
3. **Apply cross-platform conversion** when executing commands in different environments
4. **Create directories automatically** with `mkdir(parents=True, exist_ok=True)`
5. **Test on both Windows and WSL** to ensure compatibility

## Testing

Run the cross-platform test to verify the structure:
```bash
python test_cross_platform_paths.py
```

This will validate all paths exist and show both Windows and WSL path formats.
