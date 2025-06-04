#!/usr/bin/env python3
"""
Advanced formatting fixes for A2 Robot documentation.
Handles header spacing, metadata blocks, and other complex formatting issues.
"""

import os
import re
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import json

def fix_header_spacing(content: str) -> Tuple[str, List[str]]:
    """Fix headers missing space after #"""
    changes = []
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        # Match headers without space after #
        match = re.match(r'^(#{1,6})([^#\s].*)', line)
        if match:
            level = match.group(1)
            text = match.group(2)
            lines[i] = f"{level} {text}"
            changes.append(f"Line {i+1}: Fixed header spacing")
    
    return '\n'.join(lines), changes

def should_have_metadata(filepath: str, content: str) -> bool:
    """Determine if a file should have metadata block"""
    filename = os.path.basename(filepath).lower()
    
    # Skip certain file types
    skip_patterns = [
        'readme.md',
        'index.md',
        'toc.md',
        'changelog.md',
        'license.md'
    ]
    
    if any(pattern in filename for pattern in skip_patterns):
        return False
    
    # Skip files in archive directories
    if '/archive/' in filepath or '/deprecated/' in filepath:
        return False
    
    # Skip very short files (less than 10 lines)
    if len(content.split('\n')) < 10:
        return False
    
    # Skip files that already have metadata
    if content.strip().startswith('---'):
        return False
    
    return True

def generate_metadata_block(filepath: str, content: str) -> str:
    """Generate appropriate metadata block for a document"""
    filename = os.path.basename(filepath)
    title = filename.replace('.md', '').replace('_', ' ').replace('-', ' ').title()
    
    # Determine document type
    doc_type = "guide"
    if any(word in filename.lower() for word in ['design', 'architecture', 'spec']):
        doc_type = "design"
    elif any(word in filename.lower() for word in ['api', 'interface']):
        doc_type = "api"
    elif any(word in filename.lower() for word in ['test', 'calibration']):
        doc_type = "specification"
    elif any(word in filename.lower() for word in ['implementation', 'setup']):
        doc_type = "guide"
    
    # Determine status
    status = "active"
    if '/archive/' in filepath or '/deprecated/' in filepath:
        status = "archived"
    elif 'draft' in filename.lower() or 'wip' in filename.lower():
        status = "draft"
    
    metadata = f"""---
title: "{title}"
type: {doc_type}
status: {status}
created: "2024-01-01"
updated: "2024-01-01"
---

"""
    return metadata

def add_metadata_blocks(content: str, filepath: str) -> Tuple[str, List[str]]:
    """Add metadata blocks to appropriate documents"""
    changes = []
    
    if should_have_metadata(filepath, content):
        metadata = generate_metadata_block(filepath, content)
        content = metadata + content
        changes.append("Added metadata block")
    
    return content, changes

def fix_code_block_languages(content: str) -> Tuple[str, List[str]]:
    """Add language specifications to code blocks where obvious"""
    changes = []
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        if line.strip() == '```':
            # Look at the next few lines to guess the language
            next_lines = lines[i+1:i+5]
            language = guess_code_language(next_lines)
            if language:
                lines[i] = f'```{language}'
                changes.append(f"Line {i+1}: Added language specification '{language}'")
    
    return '\n'.join(lines), changes

def guess_code_language(lines: List[str]) -> Optional[str]:
    """Guess the programming language from code content"""
    content = '\n'.join(lines).lower()
    
    # Python indicators
    if any(keyword in content for keyword in ['def ', 'import ', 'from ', 'class ', 'if __name__']):
        return 'python'
    
    # Bash/shell indicators
    if any(indicator in content for indicator in ['#!/bin/bash', '#!/bin/sh', 'sudo ', 'apt-get', 'cd ', 'ls ', 'mkdir']):
        return 'bash'
    
    # C++ indicators
    if any(keyword in content for keyword in ['#include', 'void setup()', 'void loop()', 'arduino']):
        return 'cpp'
    
    # YAML indicators
    if any(indicator in content for indicator in ['version:', 'services:', 'volumes:', 'environment:']):
        return 'yaml'
    
    # JSON indicators
    if content.strip().startswith('{') and '"' in content:
        return 'json'
    
    # XML indicators
    if '<' in content and '>' in content and content.strip().startswith('<'):
        return 'xml'
    
    return None

def process_file(filepath: str, dry_run: bool = False) -> Dict:
    """Process a single markdown file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        content = original_content
        all_changes = []
        
        # Apply fixes in order
        content, changes = fix_header_spacing(content)
        all_changes.extend(changes)
        
        content, changes = add_metadata_blocks(content, filepath)
        all_changes.extend(changes)
        
        content, changes = fix_code_block_languages(content)
        all_changes.extend(changes)
        
        # Write back if changes were made and not dry run
        if all_changes and not dry_run:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        
        return {
            'file': filepath,
            'changes': all_changes,
            'success': True
        }
    
    except Exception as e:
        return {
            'file': filepath,
            'changes': [],
            'success': False,
            'error': str(e)
        }

def main():
    parser = argparse.ArgumentParser(description='Advanced formatting fixes for A2 Robot documentation')
    parser.add_argument('--directory', default='a2-docs', help='Directory to process')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without making changes')
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
    
    results = []
    total_changes = 0
    modified_files = 0
    
    for filepath in files_to_process:
        result = process_file(filepath, args.dry_run)
        results.append(result)
        
        if result['success']:
            if result['changes']:
                modified_files += 1
                total_changes += len(result['changes'])
                status = "Would fix" if args.dry_run else "Fixed"
                print(f"✅ {status} {result['file']}")
                for change in result['changes']:
                    print(f"   - {change}")
            else:
                print(f"✅ No changes needed for {result['file']}")
        else:
            print(f"❌ Error processing {result['file']}: {result['error']}")
    
    # Summary
    action = "would be modified" if args.dry_run else "modified"
    print(f"\n📊 Summary: {len(files_to_process)}/{len(files_to_process)} files processed successfully")
    print(f"{modified_files} files {action} with {total_changes} total changes.")

if __name__ == '__main__':
    main() 