#!/usr/bin/env python3
"""
Fix remaining common warnings in documentation.
"""

import os
import re
from typing import List, Tuple

def fix_code_block_languages(content: str) -> Tuple[str, List[str]]:
    """Add language specifications to code blocks where possible."""
    changes = []
    
    # More comprehensive language detection patterns
    patterns = [
        # Python
        (r'```\n(#!/usr/bin/env python|#!/usr/bin/python|import |from |def |class |if __name__|print\()', r'```python\n\1'),
        # Bash/Shell
        (r'```\n(#!/bin/bash|#!/bin/sh|\$ |sudo |apt |pip install|npm |cd |ls |mkdir |chmod)', r'```bash\n\1'),
        # JSON
        (r'```\n(\s*\{[\s\S]*?"[^"]*":\s*)', r'```json\n\1'),
        # YAML
        (r'```\n([a-zA-Z_][a-zA-Z0-9_]*:\s*\n|\s*-\s+[a-zA-Z]|version:|services:|environment:)', r'```yaml\n\1'),
        # HTML
        (r'```\n(<[^>]+>|<!DOCTYPE)', r'```html\n\1'),
        # SQL
        (r'```\n(SELECT |INSERT |UPDATE |DELETE |CREATE |ALTER )', r'```sql\n\1'),
        # C++/Arduino
        (r'```\n(#include|void setup\(\)|void loop\(\)|digitalWrite|digitalRead)', r'```cpp\n\1'),
        # Markdown
        (r'```\n(# |## |### |\[.*\]\(.*\))', r'```markdown\n\1'),
        # XML
        (r'```\n(<\?xml|<[a-zA-Z][^>]*>)', r'```xml\n\1'),
    ]
    
    for pattern, replacement in patterns:
        new_content = re.sub(pattern, replacement, content, flags=re.IGNORECASE | re.MULTILINE)
        if new_content != content:
            changes.append("Fixed code block language specification")
            content = new_content
            break  # Only apply first match to avoid conflicts
    
    return content, changes

def add_overview_section(content: str, filepath: str) -> Tuple[str, List[str]]:
    """Add Overview section if missing."""
    changes = []
    
    # Check if Overview section already exists
    if '## Overview' in content or '# Overview' in content:
        return content, changes
    
    lines = content.split('\n')
    
    # Find the first header after metadata
    insert_line = -1
    in_yaml = False
    
    for i, line in enumerate(lines):
        if line.strip() == '---':
            in_yaml = not in_yaml
            continue
        
        if not in_yaml and line.startswith('# '):
            # Found main title, insert Overview after it
            insert_line = i + 1
            break
    
    if insert_line > 0:
        # Generate appropriate overview text based on filename
        filename = os.path.basename(filepath)
        
        if 'guide' in filename.lower():
            overview_text = "This guide provides step-by-step instructions for implementation and configuration."
        elif 'design' in filename.lower():
            overview_text = "This document outlines the design architecture and implementation approach."
        elif 'spec' in filename.lower():
            overview_text = "This specification defines the technical requirements and constraints."
        elif 'api' in filename.lower():
            overview_text = "This document describes the API interfaces and usage patterns."
        else:
            overview_text = "This document provides detailed information and implementation guidance."
        
        overview_section = [
            "",
            "## Overview",
            "",
            overview_text,
            ""
        ]
        
        # Insert overview section
        for j, overview_line in enumerate(overview_section):
            lines.insert(insert_line + j, overview_line)
        
        changes.append("Added Overview section")
        content = '\n'.join(lines)
    
    return content, changes

def add_table_of_contents(content: str) -> Tuple[str, List[str]]:
    """Add Table of Contents for long documents."""
    changes = []
    
    # Check if TOC already exists
    if 'Table of Contents' in content or '## Contents' in content:
        return content, changes
    
    lines = content.split('\n')
    
    # Only add TOC if document is long (>100 lines) and has multiple sections
    if len(lines) < 100:
        return content, changes
    
    # Extract headers
    headers = []
    for line in lines:
        if re.match(r'^#{2,4}\s+', line):  # Level 2-4 headers
            level = len(line) - len(line.lstrip('#'))
            text = line.strip('#').strip()
            anchor = text.lower().replace(' ', '-').replace('(', '').replace(')', '').replace(',', '').replace('.', '')
            headers.append((level, text, anchor))
    
    # Only add TOC if there are enough sections
    if len(headers) < 3:
        return content, changes
    
    # Find where to insert TOC (after Overview section if it exists)
    insert_line = -1
    in_yaml = False
    
    for i, line in enumerate(lines):
        if line.strip() == '---':
            in_yaml = not in_yaml
            continue
        
        if not in_yaml:
            if line.startswith('## Overview'):
                # Find end of Overview section
                for j in range(i + 1, len(lines)):
                    if lines[j].startswith('##'):
                        insert_line = j
                        break
                break
            elif line.startswith('# ') and insert_line == -1:
                # No Overview section, insert after main title
                insert_line = i + 1
    
    if insert_line > 0:
        toc_lines = [
            "",
            "## Table of Contents",
            ""
        ]
        
        for level, text, anchor in headers:
            indent = "  " * (level - 2)  # Level 2 = no indent, Level 3 = 2 spaces, etc.
            toc_lines.append(f"{indent}- [{text}](#{anchor})")
        
        toc_lines.append("")
        toc_lines.append("---")
        toc_lines.append("")
        
        # Insert TOC
        for j, toc_line in enumerate(toc_lines):
            lines.insert(insert_line + j, toc_line)
        
        changes.append("Added Table of Contents")
        content = '\n'.join(lines)
    
    return content, changes

def process_file(filepath: str, dry_run: bool = False) -> dict:
    """Process a single file to fix warnings."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            original_content = f.read()
    except Exception as e:
        return {
            'file': filepath,
            'changes': [],
            'success': False,
            'error': str(e)
        }
    
    content = original_content
    all_changes = []
    
    # Apply fixes
    content, changes = fix_code_block_languages(content)
    all_changes.extend(changes)
    
    content, changes = add_overview_section(content, filepath)
    all_changes.extend(changes)
    
    content, changes = add_table_of_contents(content)
    all_changes.extend(changes)
    
    # Write back if changes were made and not dry run
    if all_changes and not dry_run:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            return {
                'file': filepath,
                'changes': all_changes,
                'success': False,
                'error': str(e)
            }
    
    return {
        'file': filepath,
        'changes': all_changes,
        'success': True
    }

def main():
    """Fix remaining warnings in documentation."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Fix remaining warnings in A2 Robot documentation')
    parser.add_argument('--directory', default='a2-docs', help='Directory to process')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed')
    parser.add_argument('--files', nargs='*', help='Specific files to process')
    
    args = parser.parse_args()
    
    # Collect files to process
    files_to_process = []
    
    if args.files:
        files_to_process = [f for f in args.files if f.endswith('.md')]
    else:
        for root, dirs, files in os.walk(args.directory):
            for file in files:
                if file.endswith('.md'):
                    files_to_process.append(os.path.join(root, file))
    
    if not files_to_process:
        print("No markdown files found to process.")
        return
    
    print(f"🔧 {'Analyzing' if args.dry_run else 'Processing'} {len(files_to_process)} markdown files...")
    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
    
    total_changes = 0
    modified_files = 0
    
    for filepath in files_to_process:
        result = process_file(filepath, args.dry_run)
        
        if result['success']:
            if result['changes']:
                modified_files += 1
                total_changes += len(result['changes'])
                status = "Would fix" if args.dry_run else "Fixed"
                print(f"✅ {status} {result['file']}")
                for change in result['changes']:
                    print(f"   - {change}")
        else:
            print(f"❌ Error processing {result['file']}: {result.get('error', 'Unknown error')}")
    
    # Summary
    action = "would be modified" if args.dry_run else "modified"
    print(f"\n📊 Summary: {modified_files} files {action} with {total_changes} total changes.")

if __name__ == '__main__':
    main() 