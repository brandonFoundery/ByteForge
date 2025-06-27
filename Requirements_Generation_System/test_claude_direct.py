#!/usr/bin/env python3
"""
Test Claude Code directly with immediate feedback
"""

import subprocess
import time
from pathlib import Path
from rich.console import Console

console = Console()


def test_claude_direct():
    """Test Claude Code with a very specific, immediate task"""
    
    console.print("[bold blue]Testing Claude Code with Direct File Creation[/bold blue]")
    
    base_path = Path("D:/Repository/@Clients/FY.WB.Midway")
    
    # Create a very specific, simple prompt
    prompt = """Please create a simple React component file right now.

SPECIFIC TASK:
Create the file: FrontEnd/src/components/TestComponent.tsx

EXACT CONTENT:
```typescript
import React from 'react';

interface TestComponentProps {
  message?: string;
}

const TestComponent: React.FC<TestComponentProps> = ({ message = "Hello from Claude Code!" }) => {
  return (
    <div className="p-4 bg-blue-100 rounded-lg">
      <h2 className="text-xl font-bold text-blue-800">Test Component</h2>
      <p className="text-blue-600">{message}</p>
      <p className="text-sm text-gray-500">Created by Claude Code at {new Date().toLocaleString()}</p>
    </div>
  );
};

export default TestComponent;
```

Please create this file NOW and confirm it was created. Show me the file path and contents.
"""
    
    # Convert paths to WSL format
    wsl_base_path = str(base_path).replace("\\", "/").replace("D:", "/mnt/d")
    
    console.print(f"[yellow]Executing Claude Code with direct file creation task...[/yellow]")
    console.print(f"[dim]Base path: {wsl_base_path}[/dim]")
    
    try:
        # Execute Claude Code directly
        result = subprocess.run([
            "wsl", "-d", "Ubuntu", "-e", "bash", "-c",
            f'cd {wsl_base_path} && claude --model sonnet --dangerously-skip-permissions -p "{prompt}"'
        ], capture_output=True, text=True, timeout=120)
        
        console.print(f"[green]Exit code: {result.returncode}[/green]")
        
        if result.stdout:
            console.print(f"[blue]Claude Code Output:[/blue]")
            console.print(result.stdout)
        
        if result.stderr:
            console.print(f"[red]Claude Code Errors:[/red]")
            console.print(result.stderr)
        
        # Check if the file was created
        test_file = base_path / "FrontEnd" / "src" / "components" / "TestComponent.tsx"
        console.print(f"\n[bold]Checking if file was created:[/bold]")
        console.print(f"[dim]Expected path: {test_file}[/dim]")
        
        if test_file.exists():
            console.print(f"[green]✅ File created successfully![/green]")
            console.print(f"[green]File size: {test_file.stat().st_size} bytes[/green]")
            
            # Show file contents
            with open(test_file, 'r') as f:
                content = f.read()
            console.print(f"[blue]File contents:[/blue]")
            console.print(content[:500] + "..." if len(content) > 500 else content)
        else:
            console.print(f"[red]❌ File was not created[/red]")
            
            # Check if components directory exists
            components_dir = base_path / "FrontEnd" / "src" / "components"
            if components_dir.exists():
                console.print(f"[yellow]Components directory exists[/yellow]")
                existing_files = list(components_dir.glob("*.tsx"))
                console.print(f"[yellow]Existing .tsx files: {len(existing_files)}[/yellow]")
                for file in existing_files[:5]:
                    console.print(f"  • {file.name}")
            else:
                console.print(f"[red]Components directory does not exist[/red]")
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        console.print(f"[red]❌ Claude Code execution timed out after 120 seconds[/red]")
        return False
    except Exception as e:
        console.print(f"[red]❌ Error executing Claude Code: {e}[/red]")
        return False


def main():
    """Main function"""
    
    console.print("[bold]🧪 Direct Claude Code File Creation Test[/bold]")
    console.print("[dim]This will test if Claude Code can create a specific file immediately[/dim]\n")
    
    success = test_claude_direct()
    
    if success:
        console.print("\n[green]🎉 Test completed successfully![/green]")
    else:
        console.print("\n[red]❌ Test failed[/red]")
        console.print("[yellow]💡 This helps us understand why files aren't being created[/yellow]")


if __name__ == "__main__":
    main()
