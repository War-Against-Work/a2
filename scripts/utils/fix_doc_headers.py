#!/usr/bin/env python3
"""Add standard headers to documents missing them."""

import re
from pathlib import Path
from datetime import datetime

def add_standard_header(file_path: Path):
    """Add standard header to document."""
    content = file_path.read_text()
    
    # Check if already has header
    if "Document Status:" in content:
        return False
    
    # Extract title (first line)
    lines = content.split('\n')
    title = lines[0].strip('# ')
    
    # Determine document type
    doc_type = "CURRENT"
    if "deprecated" in str(file_path).lower():
        doc_type = "DEPRECATED"
    elif "draft" in str(file_path).lower():
        doc_type = "DRAFT"
    
    # Create header
    header = f"""# {title}

> **Document Status:** {doc_type}  
> **Last Updated:** {datetime.now().strftime('%Y-%m-%d')}  
> **Version:** 1.0.0  
> **Scope:** Phase 1

"""
    
    # Reconstruct document
    new_content = header + '\n'.join(lines[1:])
    
    # Save
    file_path.write_text(new_content)
    return True

def fix_all_headers():
    """Fix headers in all documents."""
    doc_dir = Path("/home/waragainstwork/A2/a2-docs")
    
    fixed = 0
    for md_file in doc_dir.glob("*.md"):
        if md_file.name in ["README.md", "DOCUMENTATION_INDEX.md"]:
            continue
            
        if add_standard_header(md_file):
            print(f"✓ Fixed header: {md_file.name}")
            fixed += 1
    
    print(f"\n✅ Fixed {fixed} document headers")

if __name__ == "__main__":
    fix_all_headers()