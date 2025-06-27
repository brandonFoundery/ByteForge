import json
import yaml
from pathlib import Path
import re
from collections import defaultdict, deque
import networkx as nx
import matplotlib.pyplot as plt
from rich.console import Console
from rich.table import Table
from rich.tree import Tree
from rich import print as rprint

console = Console()


class TraceabilityAnalyzer:
    """Analyze and validate traceability between requirements documents"""
    
    def __init__(self, documents_path: Path):
        self.documents_path = Path(documents_path)
        self.trace_map = defaultdict(lambda: {"to": set(), "from": set()})
        self.documents = {}
        
    def extract_ids_from_content(self, content: str) -> set:
        """Extract requirement IDs from document content"""
        # Pattern to match various ID formats
        patterns = [
            r'BRD-\d+(?:\.\d+)*',
            r'PRD-\d+(?:\.\d+)*',
            r'FRD-\d+(?:\.\d+)*',
            r'NFRD-\d+(?:\.\d+)*',
            r'DRD-\d+(?:\.\d+)*',
            r'TRD-\d+(?:\.\d+)*',
            r'TC-\d+(?:\.\d+)*',
            r'API-\d+(?:\.\d+)*',
            r'DB-\d+(?:\.\d+)*'
        ]
        
        ids = set()
        for pattern in patterns:
            ids.update(re.findall(pattern, content))
            
        return ids
    
    def load_documents(self):
        """Load all documents and build traceability map"""
        console.print("[cyan]Loading documents and analyzing traceability...[/cyan]")
        
        for doc_file in self.documents_path.glob("*.md"):
            if doc_file.name == "status_report.txt":
                continue
                
            content = doc_file.read_text(encoding='utf-8')
            
            # Extract metadata
            if content.startswith("---"):
                metadata_end = content.find("---", 3)
                if metadata_end > 0:
                    metadata = yaml.safe_load(content[3:metadata_end])
                    doc_id = metadata.get("id", doc_file.stem)
                    self.documents[doc_id] = {
                        "file": doc_file,
                        "title": metadata.get("title", "Unknown"),
                        "metadata": metadata,
                        "content": content[metadata_end + 3:]
                    }
                    
                    # Extract all referenced IDs
                    referenced_ids = self.extract_ids_from_content(content)
                    
                    # Build traceability map
                    for ref_id in referenced_ids:
                        if ref_id != doc_id:  # Don't self-reference
                            self.trace_map[doc_id]["to"].add(ref_id)
                            self.trace_map[ref_id]["from"].add(doc_id)
    
    def analyze_traceability(self):
        """Analyze and report on traceability"""
        self.load_documents()
        
        console.print("\n[bold]Traceability Analysis Report[/bold]\n")
        
        # Create summary table
        table = Table(title="Document Traceability Summary")
        table.add_column("Document", style="cyan")
        table.add_column("Traces To", style="green")
        table.add_column("Traced From", style="blue")
        table.add_column("Coverage", style="yellow")
        
        for doc_id in sorted(self.documents.keys()):
            traces_to = len(self.trace_map[doc_id]["to"])
            traced_from = len(self.trace_map[doc_id]["from"])
            total_traces = traces_to + traced_from
            
            if total_traces > 0:
                coverage = "✅ Connected"
            else:
                coverage = "⚠️ Isolated"
                
            table.add_row(
                doc_id,
                str(traces_to),
                str(traced_from),
                coverage
            )
            
        console.print(table)
        
        # Find orphaned requirements
        self.find_orphaned_requirements()
        
        # Check for circular dependencies
        self.check_circular_dependencies()
        
        # Generate traceability tree
        self.generate_traceability_tree()
        
    def find_orphaned_requirements(self):
        """Find requirements with no traceability"""
        console.print("\n[bold]Orphaned Requirements Analysis[/bold]")
        
        orphaned = []
        
        for doc_id in self.documents:
            if (len(self.trace_map[doc_id]["to"]) == 0 and 
                len(self.trace_map[doc_id]["from"]) == 0):
                orphaned.append(doc_id)
                
        if orphaned:
            console.print(f"\n[yellow]Found {len(orphaned)} orphaned documents:[/yellow]")
            for doc in orphaned:
                console.print(f"  - {doc}: {self.documents[doc]['title']}")
        else:
            console.print("\n[green]✅ No orphaned documents found![/green]")
            
    def check_circular_dependencies(self):
        """Check for circular dependencies in traceability"""
        console.print("\n[bold]Circular Dependency Check[/bold]")
        
        # Build directed graph
        G = nx.DiGraph()
        for doc_id, traces in self.trace_map.items():
            for target in traces["to"]:
                G.add_edge(doc_id, target)
                
        # Find cycles
        try:
            cycles = list(nx.simple_cycles(G))
            if cycles:
                console.print(f"\n[red]⚠️ Found {len(cycles)} circular dependencies:[/red]")
                for cycle in cycles:
                    console.print(f"  Cycle: {' -> '.join(cycle)} -> {cycle[0]}")
            else:
                console.print("\n[green]✅ No circular dependencies found![/green]")
        except:
            console.print("\n[green]✅ No circular dependencies found![/green]")
            
    def generate_traceability_tree(self):
        """Generate a visual tree of traceability"""
        console.print("\n[bold]Traceability Tree[/bold]")
        
        # Find root documents (no incoming traces)
        roots = []
        for doc_id in self.documents:
            if len(self.trace_map[doc_id]["from"]) == 0:
                roots.append(doc_id)
                
        if not roots:
            # If no clear roots, start with BRD
            roots = [doc for doc in self.documents if doc.startswith("BRD")]
            
        # Build tree for each root
        for root in sorted(roots):
            tree = Tree(f"[bold cyan]{root}[/bold cyan]: {self.documents.get(root, {}).get('title', 'Unknown')}")
            self._build_tree_branch(tree, root, set())
            rprint(tree)
            
    def _build_tree_branch(self, parent_node, doc_id, visited):
        """Recursively build tree branches"""
        if doc_id in visited:
            return
            
        visited.add(doc_id)
        
        for child_id in sorted(self.trace_map[doc_id]["to"]):
            if child_id in self.documents:
                child_title = self.documents[child_id]["title"]
                child_node = parent_node.add(f"[green]{child_id}[/green]: {child_title}")
                
                if child_id not in visited:
                    self._build_tree_branch(child_node, child_id, visited)
                else:
                    child_node.add("[yellow]↺ (circular reference)[/yellow]")
                    
    def export_traceability_matrix(self, output_file: Path):
        """Export traceability as a CSV matrix"""
        console.print(f"\n[cyan]Exporting traceability matrix to {output_file}...[/cyan]")
        
        # Get all document IDs
        all_docs = sorted(set(self.documents.keys()) | set(self.trace_map.keys()))
        
        # Create matrix
        with open(output_file, 'w', encoding='utf-8') as f:
            # Header
            f.write("Source/Target," + ",".join(all_docs) + "\n")
            
            # Rows
            for source in all_docs:
                row = [source]
                for target in all_docs:
                    if target in self.trace_map[source]["to"]:
                        row.append("X")
                    else:
                        row.append("")
                f.write(",".join(row) + "\n")
                
        console.print(f"[green]✅ Matrix exported to {output_file}[/green]")
        
    def visualize_traceability_graph(self, output_file: Path):
        """Create a visual graph of traceability relationships"""
        console.print(f"\n[cyan]Creating traceability graph visualization...[/cyan]")
        
        # Build graph
        G = nx.DiGraph()
        
        # Add nodes
        for doc_id, doc_info in self.documents.items():
            G.add_node(doc_id, title=doc_info["title"])
            
        # Add edges
        for source, traces in self.trace_map.items():
            for target in traces["to"]:
                if target in self.documents:  # Only add if target exists
                    G.add_edge(source, target)
                    
        # Create visualization
        plt.figure(figsize=(15, 10))
        
        # Define positions using hierarchical layout
        try:
            pos = nx.spring_layout(G, k=3, iterations=50)
        except:
            pos = nx.circular_layout(G)
            
        # Define colors by document type
        color_map = {
            'BRD': '#FF6B6B',
            'PRD': '#4ECDC4',
            'FRD': '#45B7D1',
            'NFRD': '#96CEB4',
            'DRD': '#DDA0DD',
            'TRD': '#F9CA24',
            'API': '#6C5CE7',
            'DB': '#A29BFE',
            'TEST': '#FD79A8',
            'RTM': '#FAB1A0'
        }
        
        node_colors = []
        for node in G.nodes():
            prefix = node.split('-')[0]
            node_colors.append(color_map.get(prefix, '#95A5A6'))
            
        # Draw graph
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=3000, alpha=0.9)
        nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')
        nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True, arrowsize=20, alpha=0.5)
        
        plt.title("Requirements Traceability Graph", fontsize=16, fontweight='bold')
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        console.print(f"[green]✅ Graph saved to {output_file}[/green]")


def validate_document_structure(doc_path: Path):
    """Validate the structure of a generated document"""
    console.print(f"\n[cyan]Validating document: {doc_path.name}[/cyan]")
    
    content = doc_path.read_text(encoding='utf-8')
    issues = []
    
    # Check for metadata
    if not content.startswith("---"):
        issues.append("Missing YAML metadata header")
    else:
        metadata_end = content.find("---", 3)
        if metadata_end < 0:
            issues.append("Incomplete metadata section")
        else:
            try:
                metadata = yaml.safe_load(content[3:metadata_end])
                required_fields = ["id", "title", "version", "generated_at", "status"]
                for field in required_fields:
                    if field not in metadata:
                        issues.append(f"Missing metadata field: {field}")
            except:
                issues.append("Invalid YAML metadata")
                
    # Check for required sections based on document type
    doc_type = doc_path.stem
    
    if "BRD" in doc_type:
        required_sections = ["Executive Summary", "Business Objectives", "Success Metrics"]
    elif "PRD" in doc_type:
        required_sections = ["Product Overview", "Features", "User Stories"]
    elif "FRD" in doc_type:
        required_sections = ["Functional Requirements", "System Components"]
    else:
        required_sections = []
        
    for section in required_sections:
        if section not in content:
            issues.append(f"Missing required section: {section}")
            
    # Report results
    if issues:
        console.print(f"[yellow]⚠️ Found {len(issues)} issues:[/yellow]")
        for issue in issues:
            console.print(f"  - {issue}")
    else:
        console.print("[green]✅ Document structure is valid![/green]")
        
    return len(issues) == 0


def main():
    """Main utility functions"""
    import sys
    
    if len(sys.argv) < 2:
        console.print("[bold]Requirements Generation Utilities[/bold]\n")
        console.print("Usage:")
        console.print("  python utils.py analyze [documents_path]    - Analyze traceability")
        console.print("  python utils.py validate [document_path]    - Validate document structure")
        console.print("  python utils.py export [documents_path]     - Export traceability matrix")
        console.print("  python utils.py graph [documents_path]      - Create traceability graph")
        return
        
    command = sys.argv[1]
    
    if command == "analyze":
        path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("d:/Repository/@Clients/FY.WB.Midway/generated_documents")
        analyzer = TraceabilityAnalyzer(path)
        analyzer.analyze_traceability()
        
    elif command == "validate":
        if len(sys.argv) < 3:
            console.print("[red]Please provide document path[/red]")
            return
        doc_path = Path(sys.argv[2])
        validate_document_structure(doc_path)
        
    elif command == "export":
        path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("d:/Repository/@Clients/FY.WB.Midway/generated_documents")
        analyzer = TraceabilityAnalyzer(path)
        analyzer.load_documents()
        analyzer.export_traceability_matrix(path / "traceability_matrix.csv")
        
    elif command == "graph":
        path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("d:/Repository/@Clients/FY.WB.Midway/generated_documents")
        analyzer = TraceabilityAnalyzer(path)
        analyzer.load_documents()
        analyzer.visualize_traceability_graph(path / "traceability_graph.png")
        
    else:
        console.print(f"[red]Unknown command: {command}[/red]")


if __name__ == "__main__":
    main()